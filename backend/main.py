import logging
import json
import os
import sys

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
from utils.dates import get_current_month_str
from services import dashboard_service, etm_service, live_service, slot_service, analyst_service
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
def init_data():
    if use_mock:
        return mock_store.get_init()
    try:
        filters = {}
        for col, key in [
            ("Analyst_Email", "analysts"),
            ("TL_Name", "tls"),
            ("AM", "ams"),
            ("QA_Name", "qas"),
            ("Category", "categories"),
            ("Location", "locations"),
            ("Month", "months"),
        ]:
            try:
                rows = fetch_all(f"SELECT DISTINCT {col} FROM vw_dashboard_consolidated WHERE {col} IS NOT NULL ORDER BY {col}")
                filters[key] = [r.get(col) for r in rows if r.get(col) is not None]
            except Exception as e:
                logger.warning(f"Could not load filter {col}: {e}")
                filters[key] = []

        total_rows = fetch_all("SELECT COUNT(*) AS cnt FROM vw_dashboard_consolidated")[0].get("cnt", 0)
        date_range = fetch_all("SELECT MIN(Date) AS minDate, MAX(Date) AS maxDate FROM vw_dashboard_consolidated")
        dr = date_range[0] if date_range else {}
        latest_month_rows = fetch_all("""
            SELECT TOP 1 Month
            FROM vw_dashboard_consolidated
            WHERE Month IS NOT NULL
            ORDER BY TRY_CONVERT(date, Date, 106) DESC
        """)
        current_month = (
            latest_month_rows[0].get("Month")
            if latest_month_rows and latest_month_rows[0].get("Month")
            else get_current_month_str()
        )
        return {
            "success": True,
            "filters": filters,
            "totalRows": total_rows,
            "minDate": dr.get("minDate"),
            "maxDate": dr.get("maxDate"),
            "currentMonth": current_month,
            "source": "SQL Server"
        }
    except Exception as e:
        logger.error(f"Init failed: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/dashboard")
def dashboard(filters: dict = Body(default={})):
    if use_mock:
        return mock_store.get_dashboard(filters)
    try:
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
        return mock_store.get_etm()
    try:
        cache_key = "etm"
        if cache_key in cache:
            return cache[cache_key]
        data = etm_service.get_etm_data()
        cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"ETM error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/etm")
def etm_post():
    if use_mock:
        return mock_store.get_etm()
    try:
        cache_key = "etm"
        if cache_key in cache:
            return cache[cache_key]
        data = etm_service.get_etm_data()
        cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"ETM POST error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/analyst-search")
def analyst_search(email: str = Query(...)):
    if use_mock:
        return mock_store.search_analyst(email)
    try:
        return analyst_service.search_analyst(email)
    except Exception as e:
        logger.error(f"Analyst search error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/live-dashboard")
def live_dashboard(filters: dict = Body(default={})):
    if use_mock:
        return mock_store.get_live(filters)
    try:
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
        cache_key = "attrition_" + json.dumps(filters, sort_keys=True, default=str)
        if cache_key in cache:
            return cache[cache_key]
        rows = fetch_all("SELECT * FROM vw_agent_wise")
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
