"""
Direct SQL Runner for Onfido_DB
Use this script to run ad-hoc queries, verify data, or debug issues
without needing to open SSMS. It reads credentials from .env automatically.

Usage examples:
    python scripts/direct_sql.py "SELECT TOP 5 * FROM vw_dashboard_consolidated"
    python scripts/direct_sql.py "SELECT COUNT(*) AS cnt FROM stg_consolidated"
    python scripts/direct_sql.py "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='stg_consolidated'"
"""
import os
import sys
import argparse

# Ensure backend is importable
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "backend"))

# Load .env explicitly so config.py can find credentials even if CWD is not project root
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_root, ".env"))
except ImportError:
    pass

from db import fetch_all, fetch_one
from sqlalchemy import text

def main():
    parser = argparse.ArgumentParser(description="Run a SQL query directly against Onfido_DB")
    parser.add_argument("query", help="SQL query string to execute")
    parser.add_argument("--one", action="store_true", help="Return only the first row")
    parser.add_argument("--param", action="append", default=[], help="Named parameters as key=value")
    args = parser.parse_args()

    params = {}
    for p in args.param:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        params[k] = v

    try:
        if args.one:
            result = fetch_one(args.query, params if params else None)
            if result is None:
                print("No rows returned.")
            else:
                for k, v in result.items():
                    print(f"{k}: {v}")
        else:
            results = fetch_all(args.query, params if params else None)
            if not results:
                print("No rows returned.")
                return
            # Print headers
            headers = list(results[0].keys())
            print("\t".join(str(h) for h in headers))
            print("-" * (len("\t".join(str(h) for h in headers)) + 10))
            for row in results:
                print("\t".join(str(row.get(h, "")) for h in headers))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
