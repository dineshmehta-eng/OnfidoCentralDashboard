import logging
import json
import os
import sys
import threading

# Ensure backend/ is on sys.path so absolute sibling imports work when run via uvicorn
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI, Body, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
import io
import datetime
import pandas as pd
from openpyxl.styles import Font
from starlette.middleware.gzip import GZipMiddleware
from cachetools import TTLCache

from config import settings
from db import fetch_all, fetch_one, check_db_objects
from filtering import clear_filter_metadata, warm_filter_metadata
from utils.dates import get_current_month_str
from services import dashboard_service, etm_service, live_service, slot_service, analyst_service
from services.sql_snapshot import clear as clear_sql_snapshots, get_rows as get_snapshot_rows, warm as warm_sql_rows
from middleware.auth import APIKeyMiddleware
from middleware.cache import CacheControlMiddleware
from middleware.logging import RequestLogMiddleware

use_mock = settings.MOCK_DB.lower() == "true"
mock_store = None
if use_mock:
    from mock_data import MockStore
    mock_store = MockStore()

cache = TTLCache(maxsize=256, ttl=settings.CACHE_TTL_SECONDS)

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
def startup_event():
    if use_mock:
        logger.info("Skipping SQL dashboard pre-warm in MOCK mode")
        return
    def warm_sql_snapshot():
        try:
            logger.info("Warming SQL consolidated snapshot in background...")
            dashboard_service.refresh_consolidated_snapshot()
            warm_filter_metadata()
            current_month = dashboard_service.get_init_data().get("currentMonth") or get_current_month_str()
            etm_service.get_etm_data({"month": current_month})
            get_snapshot_rows(
                "vw_agent_wise_" + json.dumps({"month": current_month}, sort_keys=True),
                "SELECT * FROM vw_agent_wise WHERE LTRIM(RTRIM(month)) = :month",
                False,
                {"month": current_month},
            )
            warm_sql_rows([
                ("vw_audits", "SELECT * FROM vw_audits ORDER BY synced_at DESC"),
                ("vw_poa_live", "SELECT * FROM vw_poa_live ORDER BY synced_at DESC"),
                ("vw_apr", "SELECT * FROM vw_apr ORDER BY synced_at DESC"),
                ("vw_slot_wise_performance", "SELECT * FROM vw_slot_wise_performance ORDER BY bst_slot, ist_slot"),
                ("vw_utilization", "SELECT * FROM vw_utilization ORDER BY analyst_email"),
            ])
            logger.info("SQL consolidated snapshot ready")
        except Exception as e:
            logger.warning(f"SQL consolidated snapshot warm-up failed: {e}")
    threading.Thread(target=warm_sql_snapshot, daemon=True).start()
    if os.getenv("PREWARM_DASHBOARD", "false").lower() not in ("1", "true", "yes"):
        logger.info("Skipping blocking SQL dashboard pre-warm")
        return
    try:
        logger.info("Pre-warming dashboard cache...")
        data = dashboard_service.get_dashboard_data({})
        cache["dashboard_{}"] = data
        logger.info("Dashboard cache pre-warmed successfully")
    except Exception as e:
        logger.warning(f"Dashboard pre-warm failed (will warm on first request): {e}")

app.add_middleware(RequestLogMiddleware)
# GZip disabled for localhost - compression hurts large JSON responses more than network helps
# app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CacheControlMiddleware)

origins = [o.strip() for o in settings.API_CORS_ORIGINS.split(",") if o.strip()]
allow_all_origins = "*" in origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else (origins or ["*"]),
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(APIKeyMiddleware)

@app.middleware("http")
async def private_network_cors(request, call_next):
    if (
        request.method == "OPTIONS"
        and request.headers.get("access-control-request-private-network", "").lower() == "true"
    ):
        origin = request.headers.get("origin") or "*"
        requested_headers = request.headers.get("access-control-request-headers") or "*"
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = "*" if allow_all_origins else origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = requested_headers
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

@app.get("/api/health")
def health():
    if use_mock:
        return mock_store.get_health()
    try:
        db_info = fetch_one("SELECT DB_NAME() AS database_name, GETDATE() AS server_time")
        objects = check_db_objects()
        missing_views = [k for k, v in objects.get("views", {}).items() if not v]
        missing_tables = [k for k, v in objects.get("tables", {}).items() if not v]
        any_missing = bool(missing_views or missing_tables)
        return {
            "success": True,
            "db": db_info,
            "views": objects.get("views", {}),
            "tables": objects.get("tables", {}),
            "missingViews": missing_views,
            "missingTables": missing_tables,
            "allOk": not any_missing
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"success": False, "error": str(e)})

@app.get("/api/init")
def init_data(forceRefresh: bool = Query(False)):
    if use_mock:
        return mock_store.get_init()
    try:
        if forceRefresh:
            cache.clear()
            clear_sql_snapshots()
            clear_filter_metadata()
        return dashboard_service.get_init_data(force_refresh=forceRefresh)
    except Exception as e:
        logger.error(f"Init failed: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/dashboard")
def dashboard(filters: dict = Body(default={})):
    if use_mock:
        return mock_store.get_dashboard(filters)
    try:
        if filters.get("forceRefresh"):
            cache.clear()
            clear_sql_snapshots()
            clear_filter_metadata()
        cache_key = "dashboard_" + json.dumps(filters, sort_keys=True, default=str)
        if cache_key in cache:
            return cache[cache_key]
        data = dashboard_service.get_dashboard_data(filters)
        cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/etm")
def etm():
    if use_mock:
        return mock_store.get_etm({})
    try:
        cache_key = "etm"
        if cache_key in cache:
            return cache[cache_key]
        data = etm_service.get_etm_data({})
        cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"ETM error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/etm")
def etm_post(filters: dict = Body(default={})):
    if use_mock:
        return mock_store.get_etm(filters)
    try:
        if filters.get("forceRefresh"):
            cache.clear()
            clear_sql_snapshots()
            clear_filter_metadata()
        cache_key = "etm_" + json.dumps(filters, sort_keys=True, default=str)
        if cache_key in cache:
            return cache[cache_key]
        data = etm_service.get_etm_data(filters)
        cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"ETM POST error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/analyst-search")
def analyst_search(
    email: str = Query(...),
    month: str = Query(""),
    from_date: str = Query("", alias="from"),
    to_date: str = Query("", alias="to"),
    date_from: str = Query(""),
    date_to: str = Query(""),
    am: str = Query(""),
    tl: str = Query(""),
    qa: str = Query(""),
    category: str = Query(""),
    aon_wise: str = Query(""),
    aon: str = Query(""),
):
    if use_mock:
        return mock_store.search_analyst(email)
    try:
        filters = {
            "month": month,
            "from": from_date or date_from,
            "to": to_date or date_to,
            "am": am,
            "tl": tl,
            "qa": qa,
            "category": category,
            "aon_wise": aon_wise or aon,
        }
        return analyst_service.search_analyst(email, filters)
    except Exception as e:
        logger.error(f"Analyst search error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/live-dashboard")
def live_dashboard(filters: dict = Body(default={})):
    if use_mock:
        return mock_store.get_live(filters)
    try:
        if filters.get("forceRefresh"):
            cache.clear()
            clear_sql_snapshots()
            clear_filter_metadata()
        cache_key = "live_" + json.dumps(filters, sort_keys=True, default=str)
        if cache_key in cache:
            cached = cache[cache_key]
            if isinstance(cached, str):
                return Response(content=cached, media_type="application/json")
            return cached
        data = live_service.get_live_data(filters)
        json_str = json.dumps(data, default=str)
        cache[cache_key] = json_str
        return Response(content=json_str, media_type="application/json")
    except Exception as e:
        logger.error(f"Live dashboard error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/slot-utilization")
def slot_utilization(filters: dict = Body(default={})):
    if use_mock:
        return mock_store.get_slot_util(filters)
    try:
        if filters.get("forceRefresh"):
            cache.clear()
            clear_sql_snapshots()
            clear_filter_metadata()
        cache_key = "slot_" + json.dumps(filters, sort_keys=True, default=str)
        if cache_key in cache:
            return cache[cache_key]
        data = slot_service.get_slot_utilization(filters)
        cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"Slot utilization error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/attrition")
def attrition(filters: dict = Body(default={})):
    if use_mock:
        return mock_store.get_attrition(filters)
    try:
        if filters.get("forceRefresh"):
            cache.clear()
            clear_sql_snapshots()
            clear_filter_metadata()
        cache_key = "attrition_" + json.dumps(filters, sort_keys=True, default=str)
        if cache_key in cache:
            return cache[cache_key]
        from filtering import apply_filters, enrich_rows_with_filter_metadata, filter_value, has_dimension_filters
        sql = "SELECT * FROM vw_agent_wise"
        clauses = []
        params = {}
        month = filter_value(filters, "month", "Month")
        aon = filter_value(filters, "aon_wise", "AONWise", "aon")
        if month:
            clauses.append("LTRIM(RTRIM(month)) = :month")
            params["month"] = month
        if aon:
            clauses.append("REPLACE(LOWER(LTRIM(RTRIM(aon))), 'above then 90', 'above than 90') = :aon")
            params["aon"] = str(aon).strip().lower().replace("above then 90", "above than 90")
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        rows = get_snapshot_rows("vw_agent_wise_" + json.dumps(params, sort_keys=True), sql, bool(filters.get("forceRefresh")), params)
        if has_dimension_filters(filters):
            rows = enrich_rows_with_filter_metadata(rows)
        rows = apply_filters(rows, filters)
        data = {"success": True, "attrition": rows, "count": len(rows)}
        cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"Attrition error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/export")
def export_excel(payload: dict = Body(...)):
    tab = payload.get("tab", "export")
    data = payload.get("data", [])
    if not data:
        data = []
    df = pd.DataFrame(data)
    buf = io.BytesIO()
    sheet_name = str(tab)[:31]
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        ws = writer.sheets[sheet_name]
        for cell in ws[1]:
            cell.font = Font(bold=True)
    buf.seek(0)
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    filename = f'Onfido_{tab}_{date_str}.xlsx'
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
