import os
import pyodbc
from dotenv import load_dotenv

# Load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

SQL_SERVER = os.getenv("SQL_SERVER", "localhost\\SQLEXPRESS")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_TRUST_CERTIFICATE = os.getenv("SQL_TRUST_CERTIFICATE", "yes")
SQL_ENCRYPT = os.getenv("SQL_ENCRYPT", "no")
SQL_TRUSTED_CONNECTION = os.getenv("SQL_TRUSTED_CONNECTION", "yes")

if SQL_TRUSTED_CONNECTION.lower() in ("yes", "true", "1"):
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE=master;"
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
        f"DATABASE=master;"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
        f"TrustServerCertificate={SQL_TRUST_CERTIFICATE};"
        f"Encrypt={SQL_ENCRYPT};"
    )

conn = pyodbc.connect(conn_str, timeout=5)
cur = conn.cursor()
cur.execute("SELECT IS_SRVROLEMEMBER('sysadmin'), IS_SRVROLEMEMBER('dbcreator')")
print(cur.fetchone())
conn.close()
