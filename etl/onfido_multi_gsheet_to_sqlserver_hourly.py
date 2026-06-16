"""
Onfido Multi-GSheet to SQL Server Hourly ETL
Reads configured Google Sheets and loads into Onfido_DB staging tables.
"""
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
import sqlalchemy
from sqlalchemy import text

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("onfido_etl")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None
    logger.warning("gspread not installed. ETL will not run sheets sync.")

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

SQL_SERVER = os.getenv("SQL_SERVER", "MIS-SQL")
SQL_DATABASE = os.getenv("SQL_DATABASE", "Onfido_DB")
SQL_USERNAME = os.getenv("SQL_USERNAME", "sa")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/service_account.json")

# Sheet configurations: add your real gsheet keys and mappings here.
SHEET_CONFIGS: List[Dict[str, Any]] = [
    # Example:
    # {
    #     "sheet_name": "Consolidated",
    #     "gsheet_key": "YOUR_KEY_HERE",
    #     "worksheet": "Sheet1",
    #     "table": "stg_consolidated",
    #     "unique_cols": ["Date", "Analyst_Email"]
    # },
]


def get_sql_engine():
    import urllib.parse
    params = urllib.parse.quote_plus(
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    return sqlalchemy.create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def log_sync(table: str, rows_inserted: int, rows_updated: int, started: datetime, ended: datetime, status: str = "SUCCESS"):
    engine = get_sql_engine()
    sql = text("""
        INSERT INTO etl_sync_log (table_name, rows_inserted, rows_updated, started_at, ended_at, status)
        VALUES (:table_name, :rows_inserted, :rows_updated, :started_at, :ended_at, :status)
    """)
    try:
        with engine.connect() as conn:
            conn.execute(sql, {
                "table_name": table,
                "rows_inserted": rows_inserted,
                "rows_updated": rows_updated,
                "started_at": started,
                "ended_at": ended,
                "status": status
            })
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to write sync log: {e}")


def read_gsheet_to_df(gc, config: Dict[str, Any]) -> pd.DataFrame:
    if not gspread or not gc:
        raise RuntimeError("Google client not available")
    sh = gc.open_by_key(config["gsheet_key"])
    ws = sh.worksheet(config["worksheet"])
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    # Normalize column names
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    df.replace("", pd.NA, inplace=True)
    df = df.where(pd.notnull(df), None)
    return df


def ensure_etl_log_table(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='etl_sync_log' AND xtype='U')
                CREATE TABLE etl_sync_log (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    table_name NVARCHAR(128),
                    rows_inserted INT,
                    rows_updated INT,
                    started_at DATETIME,
                    ended_at DATETIME,
                    status NVARCHAR(50)
                )
            """))
            conn.commit()
    except Exception as e:
        logger.warning(f"etl_sync_log check/creation warning: {e}")


def upsert_to_sql(df: pd.DataFrame, table: str, unique_cols: List[str]):
    if df.empty:
        logger.info(f"No data to upsert for {table}")
        return 0, 0

    engine = get_sql_engine()
    df = df.where(pd.notnull(df), None)

    with engine.connect() as conn:
        # Simple truncate-and-load for staging tables (avoids duplicates)
        try:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            logger.info(f"Truncated {table}")
        except Exception as e:
            logger.warning(f"Could not truncate {table}: {e}. Falling back to DELETE.")
            conn.execute(text(f"DELETE FROM {table}"))

        df.to_sql(table, con=conn, if_exists="append", index=False)
        conn.commit()

    return len(df), 0


def run_sync():
    started_all = datetime.now()
    if not gspread:
        logger.error("gspread is required. Install requirements and configure service account.")
        return

    creds_path = os.path.join(os.path.dirname(__file__), "..", GOOGLE_SERVICE_ACCOUNT_FILE)
    if not os.path.exists(creds_path):
        logger.error(f"Service account file not found: {creds_path}")
        return

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)

    engine = get_sql_engine()
    ensure_etl_log_table(engine)

    for config in SHEET_CONFIGS:
        started = datetime.now()
        table = config["table"]
        try:
            logger.info(f"Processing {config['sheet_name']} -> {table}")
            df = read_gsheet_to_df(gc, config)
            inserted, updated = upsert_to_sql(df, table, config.get("unique_cols", []))
            ended = datetime.now()
            log_sync(table, inserted, updated, started, ended, "SUCCESS")
            logger.info(f"Synced {table}: {inserted} rows inserted.")
        except Exception as e:
            logger.error(f"Failed to sync {table}: {e}")
            log_sync(table, 0, 0, started, datetime.now(), "FAILED")

    logger.info(f"ETL completed in {(datetime.now() - started_all).total_seconds():.1f}s")


if __name__ == "__main__":
    run_sync()
