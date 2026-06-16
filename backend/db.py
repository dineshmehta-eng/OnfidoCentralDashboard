import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

if settings.SQL_TRUSTED_CONNECTION.lower() in ("yes", "true", "1"):
    conn_str = (
        f"DRIVER={{{settings.SQL_DRIVER}}};"
        f"SERVER={settings.SQL_SERVER};"
        f"DATABASE={settings.SQL_DATABASE};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate={settings.SQL_TRUST_CERTIFICATE};"
        f"Encrypt={settings.SQL_ENCRYPT};"
        f"Connect Timeout=10;"
    )
else:
    conn_str = (
        f"DRIVER={{{settings.SQL_DRIVER}}};"
        f"SERVER={settings.SQL_SERVER};"
        f"DATABASE={settings.SQL_DATABASE};"
        f"UID={settings.SQL_USERNAME};"
        f"PWD={settings.SQL_PASSWORD};"
        f"TrustServerCertificate={settings.SQL_TRUST_CERTIFICATE};"
        f"Encrypt={settings.SQL_ENCRYPT};"
        f"Connect Timeout=10;"
    )

params = urllib.parse.quote_plus(conn_str)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    pool_pre_ping=True,
    pool_size=settings.SQL_POOL_SIZE,
    max_overflow=settings.SQL_MAX_OVERFLOW,
    pool_recycle=settings.SQL_POOL_RECYCLE,
    isolation_level="READ COMMITTED",
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_query_timeout(dbapi_conn, connection_record):
    # Abort queries that run longer than 30 seconds to protect the pool
    dbapi_conn.timeout = 30


def fetch_all(sql: str, params: dict | None = None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        rows = result.mappings().all()
        return [dict(r) for r in rows]

def fetch_one(sql: str, params: dict | None = None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        row = result.mappings().first()
        return dict(row) if row else None


def check_db_objects() -> dict:
    """Returns existence status for required views and staging tables."""
    expected_views = [
        "vw_dashboard_consolidated", "vw_slot_wise_performance", "vw_utilization",
        "vw_audits", "vw_poa_live", "vw_apr", "vw_tqbqmq", "vw_cre",
        "vw_doc_etm", "vw_doc_task_skip", "vw_poa_etm", "vw_agent_wise"
    ]
    expected_tables = [
        "stg_consolidated", "stg_slot_wise_performance", "stg_utilization",
        "stg_audits", "stg_poa_live", "stg_apr", "stg_tqbqmq", "stg_cre",
        "stg_doc_etm", "stg_doc_task_skip", "stg_poa_etm", "stg_agent_wise",
        "etl_sync_log"
    ]
    try:
        rows = fetch_all(
            "SELECT TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo'"
        )
        existing = {r["TABLE_NAME"]: r["TABLE_TYPE"] for r in rows}
        return {
            "views": {v: v in existing and existing[v] == "VIEW" for v in expected_views},
            "tables": {t: t in existing and existing[t] == "BASE TABLE" for t in expected_tables},
        }
    except Exception as e:
        return {"views": {}, "tables": {}, "error": str(e)}
