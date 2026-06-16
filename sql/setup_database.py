import os
import sys
import pyodbc
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

SQL_SERVER = os.getenv("SQL_SERVER", "localhost\\SQLEXPRESS")
SQL_DATABASE = os.getenv("SQL_DATABASE", "Onfido_DB")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_TRUST_CERTIFICATE = os.getenv("SQL_TRUST_CERTIFICATE", "yes")
SQL_ENCRYPT = os.getenv("SQL_ENCRYPT", "no")
SQL_TRUSTED_CONNECTION = os.getenv("SQL_TRUSTED_CONNECTION", "no")

if SQL_TRUSTED_CONNECTION.lower() in ("yes", "true", "1"):
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate={SQL_TRUST_CERTIFICATE};"
        f"Encrypt={SQL_ENCRYPT};"
    )
else:
    SQL_USERNAME = os.getenv("SQL_USERNAME", "sa")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
        f"TrustServerCertificate={SQL_TRUST_CERTIFICATE};"
        f"Encrypt={SQL_ENCRYPT};"
    )

def run_sql_file(cursor, filepath):
    abs_path = os.path.join(project_root, "sql", os.path.basename(filepath))
    with open(abs_path, 'r') as f:
        sql = f.read()
    import re
    batches = [batch.strip() for batch in re.split(r'\n\s*GO\s*\n', sql, flags=re.IGNORECASE) if batch.strip()]
    for batch in batches:
        try:
            cursor.execute(batch)
            cursor.commit()
        except Exception as e:
            print(f"Warning: {e}")
            cursor.commit()

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    print(f"Connected to {SQL_DATABASE}")

    run_sql_file(cursor, 'views.sql')
    print("Views deployed")

    run_sql_file(cursor, 'repair_slot_utilization.sql')
    print("Slot/utilization repair deployed")

    run_sql_file(cursor, 'indexes.sql')
    print("Indexes deployed")

    run_sql_file(cursor, 'procedures.sql')
    print("Procedures deployed")

    conn.close()
    print("Setup complete")
except Exception as e:
    print(f"ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure the database exists. Ask a sysadmin to run:  sql/grant_permissions.sql")
    print("2. If using Windows Auth, confirm SQL_TRUSTED_CONNECTION=yes in .env")
    print("3. If using SQL auth, verify SQL_USERNAME and SQL_PASSWORD in .env")
    sys.exit(1)
