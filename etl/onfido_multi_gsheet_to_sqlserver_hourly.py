"""
Onfido Google Sheets to SQL Server hourly ETL.

The dashboard reads ETM and Task Skip from SQL views. This job keeps the
staging tables behind those views current without touching dashboard UI code.
"""
import hashlib
import json
import logging
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import sqlalchemy
from sqlalchemy import text

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("onfido_etl")

if load_dotenv:
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

SQL_SERVER = os.getenv("SQL_SERVER", "MIS-SQL")
SQL_DATABASE = os.getenv("SQL_DATABASE", "Onfido_DB")
SQL_USERNAME = os.getenv("SQL_USERNAME", "sa")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_TRUST_CERTIFICATE = os.getenv("SQL_TRUST_CERTIFICATE", "yes")
SQL_ENCRYPT = os.getenv("SQL_ENCRYPT", "no")

GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/service_account.json")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
ETL_SHEET_CONFIG_FILE = os.getenv("ETL_SHEET_CONFIG_FILE", "config/etl_sheets.json")

ETM_SPREADSHEET_ID = "1jqek7lO6f698Hos3TlgefSC8Hu67CBDkp83843cM404"
ETM_SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{ETM_SPREADSHEET_ID}/edit?gid=0#gid=0"

DEFAULT_SHEET_CONFIGS: List[Dict[str, Any]] = [
    {
        "sheet_name": "DOC ETM",
        "gsheet_key": ETM_SPREADSHEET_ID,
        "worksheet": "DOC ETM",
        "table": "stg_doc_etm",
        "spreadsheet_url": ETM_SPREADSHEET_URL,
    },
    {
        "sheet_name": "DOC Task Skip",
        "gsheet_key": ETM_SPREADSHEET_ID,
        "worksheet": "DOC Task Skip",
        "table": "stg_doc_task_skip",
        "spreadsheet_url": ETM_SPREADSHEET_URL,
    },
    {
        "sheet_name": "POA ETM",
        "gsheet_key": ETM_SPREADSHEET_ID,
        "worksheet": "POA ETM",
        "table": "stg_poa_etm",
        "spreadsheet_url": ETM_SPREADSHEET_URL,
    },
]

MANAGED_COLUMNS = {"id", "row_hash", "source_sheet", "source_spreadsheet_url", "synced_at"}


def normalize_col(value: Any) -> str:
    col = str(value or "").strip().lower()
    col = re.sub(r"[^0-9a-zA-Z]+", "_", col)
    col = re.sub(r"_+", "_", col).strip("_")
    return col


def get_sql_engine():
    import urllib.parse

    params = urllib.parse.quote_plus(
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
        f"TrustServerCertificate={SQL_TRUST_CERTIFICATE};"
        f"Encrypt={SQL_ENCRYPT};"
    )
    return sqlalchemy.create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def quote_name(name: str) -> str:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(f"Unsafe SQL identifier: {name}")
    return f"[{name}]"


def load_sheet_configs() -> List[Dict[str, Any]]:
    config_path = os.path.join(PROJECT_ROOT, ETL_SHEET_CONFIG_FILE)
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as fh:
            configs = json.load(fh)
        if not isinstance(configs, list):
            raise ValueError(f"{config_path} must contain a JSON list")
        return configs

    tables = {
        t.strip()
        for t in os.getenv("ETL_SYNC_TABLES", "stg_doc_etm,stg_doc_task_skip,stg_poa_etm").split(",")
        if t.strip()
    }
    return [cfg for cfg in DEFAULT_SHEET_CONFIGS if cfg["table"] in tables]


def get_google_client():
    if not gspread or not Credentials:
        raise RuntimeError("gspread/google-auth is not installed. Run: pip install -r backend/requirements.txt")

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", GOOGLE_SERVICE_ACCOUNT_FILE)
    if not os.path.isabs(creds_path):
        creds_path = os.path.join(PROJECT_ROOT, creds_path)
    if not os.path.exists(creds_path):
        raise FileNotFoundError(
            f"Google service account file not found: {creds_path}. "
            "Place the JSON there or set GOOGLE_SERVICE_ACCOUNT_JSON."
        )
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    return gspread.authorize(creds)


def ensure_etl_log_table(engine):
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                IF OBJECT_ID('dbo.etl_sync_log', 'U') IS NULL
                CREATE TABLE dbo.etl_sync_log (
                    id BIGINT IDENTITY(1,1) PRIMARY KEY,
                    spreadsheet_url NVARCHAR(500),
                    sheet_name NVARCHAR(128),
                    table_name NVARCHAR(128),
                    rows_read INT,
                    rows_inserted INT,
                    sync_status NVARCHAR(50),
                    error_message NVARCHAR(MAX),
                    synced_at DATETIME
                )
                """
            )
        )


def log_sync(engine, config: Dict[str, Any], rows_read: int, rows_inserted: int, status: str, error_message: str = ""):
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO dbo.etl_sync_log
                    (spreadsheet_url, sheet_name, table_name, rows_read, rows_inserted, sync_status, error_message, synced_at)
                    VALUES
                    (:spreadsheet_url, :sheet_name, :table_name, :rows_read, :rows_inserted, :sync_status, :error_message, GETDATE())
                    """
                ),
                {
                    "spreadsheet_url": config.get("spreadsheet_url", ""),
                    "sheet_name": config.get("sheet_name", config.get("worksheet", "")),
                    "table_name": config["table"],
                    "rows_read": rows_read,
                    "rows_inserted": rows_inserted,
                    "sync_status": status,
                    "error_message": error_message[:3900] if error_message else "",
                },
            )
    except Exception as exc:
        logger.error("Failed to write ETL sync log for %s: %s", config.get("table"), exc)


def read_gsheet_to_df(gc, config: Dict[str, Any]) -> pd.DataFrame:
    sh = gc.open_by_key(config["gsheet_key"])
    ws = sh.worksheet(config["worksheet"])
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame()

    headers = [normalize_col(c) for c in values[0]]
    deduped = []
    seen: Dict[str, int] = {}
    for idx, header in enumerate(headers):
        name = header or f"column_{idx + 1}"
        seen[name] = seen.get(name, 0) + 1
        deduped.append(name if seen[name] == 1 else f"{name}_{seen[name]}")

    df = pd.DataFrame(values[1:], columns=deduped)
    df = df.dropna(how="all")
    df = df.loc[:, [c for c in df.columns if not c.startswith("column_")]]
    df = df.replace("", None)
    return df.where(pd.notnull(df), None)


def table_columns(engine, table: str) -> List[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = :table
                ORDER BY ORDINAL_POSITION
                """
            ),
            {"table": table},
        ).fetchall()
    return [str(row[0]) for row in rows]


def row_hash(row: pd.Series, columns: List[str]) -> str:
    payload = "|".join("" if pd.isna(row.get(col)) else str(row.get(col)) for col in columns)
    return hashlib.sha256(payload.encode("utf-8", errors="ignore")).hexdigest()


def prepare_for_table(df: pd.DataFrame, config: Dict[str, Any], columns: List[str]) -> pd.DataFrame:
    insert_cols = [col for col in columns if col != "id"]
    source_cols = [col for col in insert_cols if col not in MANAGED_COLUMNS]

    for col in source_cols:
        if col not in df.columns:
            df[col] = None

    prepared = df[source_cols].copy()
    if "month_idx" in insert_cols and "month_idx" not in prepared:
        prepared["month_idx"] = prepared["month"] if "month" in prepared else None

    hash_cols = [col for col in source_cols if col != "month_idx"]
    if "row_hash" in insert_cols:
        prepared["row_hash"] = prepared.apply(lambda r: row_hash(r, hash_cols), axis=1)
    if "source_sheet" in insert_cols:
        prepared["source_sheet"] = config.get("sheet_name", config.get("worksheet", ""))
    if "source_spreadsheet_url" in insert_cols:
        prepared["source_spreadsheet_url"] = config.get("spreadsheet_url", "")
    if "synced_at" in insert_cols:
        prepared["synced_at"] = datetime.now()

    return prepared[[col for col in insert_cols if col in prepared.columns]]


def replace_table_data(engine, df: pd.DataFrame, config: Dict[str, Any]) -> int:
    table = config["table"]
    if df.empty:
        raise RuntimeError(f"{config['sheet_name']} returned 0 rows; keeping existing SQL data.")

    columns = table_columns(engine, table)
    if not columns:
        raise RuntimeError(f"SQL table not found or has no columns: {table}")

    prepared = prepare_for_table(df, config, columns)
    if prepared.empty:
        raise RuntimeError(f"No matching columns prepared for {table}")

    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM dbo.{quote_name(table)}"))
        prepared.to_sql(table, con=conn, schema="dbo", if_exists="append", index=False)

    return len(prepared)


def run_sync() -> int:
    started_all = datetime.now()
    configs = load_sheet_configs()
    if not configs:
        logger.warning("No ETL sheet configs found. Nothing to sync.")
        return 0

    engine = get_sql_engine()
    ensure_etl_log_table(engine)
    try:
        gc = get_google_client()
    except Exception as exc:
        logger.exception("Google Sheets client is not available")
        for config in configs:
            log_sync(engine, config, 0, 0, "Failed", str(exc))
        return len(configs)

    failures = 0
    for config in configs:
        table = config["table"]
        try:
            logger.info("Processing %s -> %s", config["sheet_name"], table)
            df = read_gsheet_to_df(gc, config)
            rows_inserted = replace_table_data(engine, df, config)
            log_sync(engine, config, len(df), rows_inserted, "Success")
            logger.info("Synced %s: %s rows.", table, rows_inserted)
        except Exception as exc:
            failures += 1
            logger.exception("Failed to sync %s", table)
            log_sync(engine, config, 0, 0, "Failed", str(exc))

    elapsed = (datetime.now() - started_all).total_seconds()
    logger.info("ETL completed in %.1fs with %s failure(s). Log: %s", elapsed, failures, log_file)
    return failures


if __name__ == "__main__":
    sys.exit(1 if run_sync() else 0)
