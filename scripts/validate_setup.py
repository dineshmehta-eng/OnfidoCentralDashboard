"""
Pre-flight validation for Onfido Dashboard deployment.
Run this before starting the app or after any environment change.

Usage:
    python scripts/validate_setup.py
"""
import os
import sys
import platform
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root / "backend"))

REQUIRED_VARS = [
    "SQL_SERVER", "SQL_DATABASE", "SQL_USERNAME", "SQL_PASSWORD", "SQL_DRIVER"
]

VIEWS = [
    "vw_dashboard_consolidated", "vw_slot_wise_performance", "vw_utilization",
    "vw_audits", "vw_poa_live", "vw_apr", "vw_tqbqmq", "vw_cre",
    "vw_doc_etm", "vw_doc_task_skip", "vw_poa_etm", "vw_agent_wise"
]

TABLES = [
    "stg_consolidated", "stg_slot_wise_performance", "stg_utilization",
    "stg_audits", "stg_poa_live", "stg_apr", "stg_tqbqmq", "stg_cre",
    "stg_doc_etm", "stg_doc_task_skip", "stg_poa_etm", "stg_agent_wise",
    "etl_sync_log"
]


def check_python():
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 10)
    print(f"  [ {'PASS' if ok else 'FAIL'} ] Python {major}.{minor} (need >= 3.10)")
    return ok


def check_odbc_driver():
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        target = [d for d in drivers if "ODBC Driver" in d and "SQL Server" in d]
        ok = bool(target)
        print(f"  [ {'PASS' if ok else 'FAIL'} ] ODBC Drivers: {target if target else 'None found'}")
        return ok
    except ImportError:
        print("  [ FAIL ] pyodbc not installed")
        return False


def check_env():
    env_path = project_root / ".env"
    if not env_path.exists():
        print("  [ FAIL ] .env file not found in project root")
        return False

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        print("  [ FAIL ] python-dotenv not installed")
        return False

    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    ok = not missing
    if ok:
        print(f"  [ PASS ] .env loaded, all {len(REQUIRED_VARS)} required variables present")
    else:
        print(f"  [ FAIL ] .env missing variables: {', '.join(missing)}")
    return ok


def check_db_connection():
    try:
        from config import settings
        import pyodbc
        conn_str = (
            f"DRIVER={{{settings.SQL_DRIVER}}};"
            f"SERVER={settings.SQL_SERVER};"
            f"DATABASE=master;"
            f"UID={settings.SQL_USERNAME};"
            f"PWD={settings.SQL_PASSWORD};"
            f"TrustServerCertificate={settings.SQL_TRUST_CERTIFICATE};"
            f"Encrypt={settings.SQL_ENCRYPT};"
            f"Connect Timeout=10;"
        )
        conn = pyodbc.connect(conn_str, timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT DB_NAME()")
        db_name = cur.fetchone()[0]
        conn.close()
        print(f"  [ PASS ] SQL Server reachable (connected to '{db_name}')")
        return True
    except Exception as e:
        print(f"  [ FAIL ] Cannot connect to SQL Server: {e}")
        return False


def check_database_exists():
    try:
        from config import settings
        import pyodbc
        conn_str = (
            f"DRIVER={{{settings.SQL_DRIVER}}};"
            f"SERVER={settings.SQL_SERVER};"
            f"DATABASE=master;"
            f"UID={settings.SQL_USERNAME};"
            f"PWD={settings.SQL_PASSWORD};"
            f"TrustServerCertificate={settings.SQL_TRUST_CERTIFICATE};"
            f"Encrypt={settings.SQL_ENCRYPT};"
            f"Connect Timeout=10;"
        )
        conn = pyodbc.connect(conn_str, timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sys.databases WHERE name = ?", settings.SQL_DATABASE)
        exists = cur.fetchone() is not None
        conn.close()
        if exists:
            print(f"  [ PASS ] Database '{settings.SQL_DATABASE}' exists")
        else:
            print(f"  [ FAIL ] Database '{settings.SQL_DATABASE}' NOT FOUND. Run sql/setup_database.py first.")
        return exists
    except Exception as e:
        print(f"  [ FAIL ] Database check skipped due to connection error: {e}")
        return False


def check_views_and_tables():
    try:
        from config import settings
        import pyodbc
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
        conn = pyodbc.connect(conn_str, timeout=10)
        cur = conn.cursor()
        cur.execute(
            "SELECT TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo'"
        )
        existing = {row.TABLE_NAME: row.TABLE_TYPE for row in cur.fetchall()}
        conn.close()

        missing_views = [v for v in VIEWS if v not in existing or existing[v] != "VIEW"]
        missing_tables = [t for t in TABLES if t not in existing or existing[t] != "BASE TABLE"]

        if not missing_views and not missing_tables:
            print(f"  [ PASS ] All {len(VIEWS)} views and {len(TABLES)} staging tables exist")
            return True
        else:
            for v in missing_views:
                print(f"  [ FAIL ] Missing view: {v}")
            for t in missing_tables:
                print(f"  [ FAIL ] Missing table: {t}")
            return False
    except Exception as e:
        print(f"  [ FAIL ] View/table check skipped: {e}")
        return False


def main():
    print("=" * 60)
    print("Onfido Dashboard -- Setup Validation")
    print("=" * 60)

    results = []
    print("\n1. Python Version")
    results.append(check_python())

    print("\n2. ODBC Driver for SQL Server")
    results.append(check_odbc_driver())

    print("\n3. Environment Variables (.env)")
    results.append(check_env())

    print("\n4. SQL Server Connectivity")
    results.append(check_db_connection())

    print("\n5. Database Existence")
    results.append(check_database_exists())

    print("\n6. Required Views and Staging Tables")
    results.append(check_views_and_tables())

    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 60)
    if passed == total:
        print(f"All checks PASSED ({passed}/{total}). Ready to start the dashboard.")
        print("Run: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
    else:
        print(f"Checks PASSED: {passed}/{total}")
        print("Please fix the FAILED items above before deploying.")
    print("=" * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
