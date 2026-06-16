import csv
import io
import os
import sys
from datetime import datetime

from fastapi import Body, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response


BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from mock_data import MockStore


app = FastAPI(title="Onfido Central Dashboard")
mock_store = MockStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return mock_store.get_health()


@app.get("/api/init")
def init_data():
    return mock_store.get_init()


@app.post("/api/dashboard")
def dashboard(filters: dict = Body(default={})):
    return mock_store.get_dashboard(filters or {})


@app.get("/api/etm")
def etm_get():
    return mock_store.get_etm()


@app.post("/api/etm")
def etm_post():
    return mock_store.get_etm()


@app.get("/api/analyst-search")
def analyst_search(email: str = Query(...)):
    return mock_store.search_analyst(email)


@app.post("/api/live-dashboard")
def live_dashboard(filters: dict = Body(default={})):
    return mock_store.get_live(filters or {})


@app.post("/api/slot-utilization")
def slot_utilization(filters: dict = Body(default={})):
    return mock_store.get_slot_util(filters or {})


@app.post("/api/attrition")
def attrition(filters: dict = Body(default={})):
    return mock_store.get_attrition(filters or {})


@app.post("/api/export")
def export_csv(payload: dict = Body(default={})):
    tab = str((payload or {}).get("tab") or "export")[:40]
    rows = (payload or {}).get("data") or []
    output = io.StringIO()
    if rows and isinstance(rows, list) and isinstance(rows[0], dict):
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    filename = f"Onfido_{tab}_{datetime.now().strftime('%Y%m%d')}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
