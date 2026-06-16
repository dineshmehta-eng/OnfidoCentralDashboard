# Onfido SQL Dashboard

Production migration of the Google Apps Script dashboard to Python FastAPI + Microsoft SQL Server.

## Project Structure

```
Onfido_SQL_Dashboard
├── backend
│   ├── main.py
│   ├── db.py
│   ├── config.py
│   ├── mock_data.py
│   ├── middleware
│   │   └── auth.py
│   ├── services
│   │   ├── dashboard_service.py
│   │   ├── etm_service.py
│   │   ├── live_service.py
│   │   ├── slot_service.py
│   │   └── analyst_service.py
│   ├── utils
│   │   ├── metrics.py
│   │   └── dates.py
│   └── requirements.txt
├── frontend
│   ├── index.html
│   └── assets
│       ├── app.js
│       └── styles.css
├── etl
│   └── onfido_multi_gsheet_to_sqlserver_hourly.py
├── sql
│   ├── views.sql
│   ├── indexes.sql
│   ├── procedures.sql
│   ├── create_db.py
│   ├── setup_database.py
│   └── check_roles.py
├── scripts
│   ├── seed_test_data.py
│   ├── direct_sql.py
│   └── install_windows_service.ps1
├── tests
│   └── loadtest_locustfile.py
├── logs
├── .env
└── README.md
```

## Prerequisites

1. **Python 3.10+**
2. **Microsoft ODBC Driver 17 or 18 for SQL Server** installed on the host.
3. **SQL Server** accessible with a login that has read/write permissions on `Onfido_DB`.
4. *(Optional for ETL)* **Google Service Account JSON** with access to the source spreadsheets.

## Setup

### 1. Configure Environment

Edit `.env` in the project root:

```env
APP_NAME=Onfido_SQL_Dashboard
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000

SQL_SERVER=YOUR_SERVER_NAME
SQL_DATABASE=Onfido_DB
SQL_USERNAME=sa
SQL_PASSWORD=YOUR_STRONG_PASSWORD
SQL_DRIVER=ODBC Driver 17 for SQL Server
SQL_TRUST_CERTIFICATE=yes
SQL_ENCRYPT=no
SQL_TRUSTED_CONNECTION=no
SQL_POOL_SIZE=20
SQL_MAX_OVERFLOW=40
SQL_POOL_RECYCLE=1800

API_CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
CACHE_TTL_SECONDS=300
LOG_LEVEL=INFO

GOOGLE_SERVICE_ACCOUNT_FILE=config/service_account.json
ETL_SYNC_INTERVAL_MINUTES=60
```

> **Security:** Never commit `.env` to version control. Rotate any default or previously shared passwords before production use.

### 2. Create Database & SQL Objects

Run the setup script from the project root:

```bash
python sql/setup_database.py
```

This script will:
- Create `Onfido_DB` if it does not exist.
- Deploy all recommended views (`sql/views.sql`).
- Deploy recommended indexes (`sql/indexes.sql`).
- Deploy helper procedures (`sql/procedures.sql`).

### 3. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Local Testing Tools

#### Mock Mode (No SQL Server Required)
Add to `.env`:
```env
MOCK_DB=true
```
Then run `uvicorn backend.main:app` and open `http://localhost:8000/`. All tabs render with synthetic data.

#### Optional API Key Authentication
Add to `.env`:
```env
API_KEY=your_strong_secret_here
```
Fill the matching constant in `frontend/assets/app.js`:
```javascript
const API_KEY = "your_strong_secret_here";  // leave empty to disable
```
When empty, no auth is enforced.

#### Direct SQL Runner
```bash
python scripts/direct_sql.py "SELECT TOP 5 * FROM vw_dashboard_consolidated"
```

#### Seed Test Data
```bash
python scripts/seed_test_data.py
```

#### Load Testing
```bash
locust -f tests/loadtest_locustfile.py --host http://localhost:8000 --headless -u 200 -r 20 -t 5m
```

### 5. Run the API

From the **project root** (not inside `backend/`):

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

For production with multiple workers (Linux example):

```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

On Windows, consider running as a service with **NSSM**, **IIS ARR**, or manually via Task Scheduler.

### 6. Verify Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"success": true, "db": {"database_name": "Onfido_DB", "server_time": "2026-06-10T..."}}
```

### 7. Open the Dashboard

Navigate to `http://localhost:8000/`. The FastAPI static-files mount serves `frontend/index.html` at the root.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Database connectivity & timestamp |
| GET | `/api/init` | Filter populations, date range, current month |
| POST | `/api/dashboard` | Overview, Productivity, Quality, POA, Trends, Alerts |
| GET | `/api/etm` | DOC ETM, POA ETM, Task Skip data |
| GET | `/api/analyst-search?email=` | Analyst search by email substring |
| POST | `/api/live-dashboard` | Live POA data |
| POST | `/api/slot-utilization` | Slot-wise performance & utilization |
| POST | `/api/attrition` | Agent-wise / attrition data |

## ETL Configuration

Configure `SHEET_CONFIGS` inside `etl/onfido_multi_gsheet_to_sqlserver_hourly.py` with your actual Google Sheet keys, worksheets, and staging table names. Example:

```python
SHEET_CONFIGS = [
    {
        "sheet_name": "Consolidated",
        "gsheet_key": "YOUR_SHEET_KEY_HERE",
        "worksheet": "Sheet1",
        "table": "stg_consolidated",
        "unique_cols": ["Date", "Analyst_Email"]
    },
    # ... add remaining sheets
]
```

Run the ETL manually:

```bash
python etl/onfido_multi_gsheet_to_sqlserver_hourly.py
```

Schedule via **Windows Task Scheduler** or **cron** to run every hour.

## Performance Tuning for 200 Concurrent Users

- **API caching:** Dashboard responses are cached for `CACHE_TTL_SECONDS` (default 300s / 5 minutes).
- **SQL Connection Pool:** Default pool size 20, max overflow 40, recycle 1800s.
- **Indexes:** `sql/indexes.sql` creates nonclustered indexes on the most common filter/aggregation columns.
- **Workers:** Start with 4 Uvicorn workers and adjust after load testing.
- **Reverse Proxy:** Deploy behind IIS ARR or Nginx for static file caching and SSL termination.
- **Static Caching:** The HTML/JS/CSS is served by FastAPI; add cache-control headers at the reverse-proxy level.

## Deployment Options

### Quick Start (Local Dev, No SQL Server)
```powershell
# Windows PowerShell
.\scripts\run_dev.ps1
```
This sets `MOCK_DB=true`, starts Uvicorn with hot-reload, and opens the browser automatically.

### Pre-Flight Validation
Before deploying anywhere, run the diagnostic script:
```bash
python scripts/validate_setup.py
```
It checks Python version, ODBC driver, `.env`, SQL Server connectivity, database existence, and all required views/tables.

### Option A: Windows Service (NSSM)
```powershell
.\scripts\install_windows_service.ps1
```
Installs the app as a Windows service with auto-start and log rotation.

### Option B: IIS Reverse Proxy (ARR)
Copy `deployment/web.config` into your IIS site root and enable ARR proxy. A maintenance page (`deployment/maintenance.html`) is shown automatically when the backend is down.

### Option C: Docker
```bash
docker build -t onfido-dashboard .
docker run -p 8000:8000 --env-file .env onfido-dashboard
```

### Option D: Linux Systemd
```bash
sudo cp deployment/onfido-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now onfido-dashboard
sudo journalctl -u onfido-dashboard -f
```

## Acceptance Checklist

- [x] HTML look and feel is unchanged (same tabs, tables, metrics, Chart.js).
- [x] Dashboard works without Google Apps Script.
- [x] No Google Sheet is read directly by dashboard.
- [x] All dashboard data comes from `Onfido_DB` via SQL views.
- [x] All filters populated from `vw_dashboard_consolidated`.
- [x] Default load uses current month when no date filter is selected.
- [x] ETM, Task Skip, Live Dashboard, Slot Utilization, and Attrition endpoints exist.
- [x] ETL uses truncate-and-load (no duplicate rows).
- [x] API caching enabled for heavy dashboard endpoint.
- [x] SQL connection pooling configured (pool=20, overflow=40).
- [x] Credentials stored only in `.env` (no hardcoded passwords in Python or HTML).
- [ ] **Load test with 200 concurrent users** (use `locust` or `k6` against `/api/dashboard`).
- [ ] **Configure `SHEET_CONFIGS`** in the ETL with real sheet keys.
- [ ] **Rotate SQL password** before production release if it was previously exposed.
- [ ] **Add authentication** if the dashboard is accessible outside the company network.

## Security Notes

- Do **not** commit `.env` to Git. Add it to `.gitignore`.
- If exposing externally, protect all endpoints with an auth layer (e.g., Windows Authentication behind IIS, OAuth2, or API key).
- Ensure the SQL login has the **minimum required permissions** (ideally `db_datareader` + `db_datawriter` for the ETL user, and `db_datareader` for the app user).

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `Health check failed` / DB connection error | ODBC driver not installed or wrong server name | Verify `SQL_SERVER` and install ODBC Driver 17/18. |
| `ModuleNotFoundError: No module named 'config'` | Running uvicorn from inside `backend/` | Run `uvicorn backend.main:app` from **project root**. |
| Frontend shows "No data available" | Views exist but staging tables are empty | Run ETL or insert test data into staging tables. |
| Filters missing | Column names in `stg_consolidated` differ from view | Verify column names match the `POSSIBLE_COLS` mapping in `dashboard_service.py`. |
| Analyst search not visible | CSS/JS mismatch | Ensure `app.js` is not cached; hard-refresh (`Ctrl+F5`). |

## Support

For questions about extending the API or adapting the frontend to other data shapes, review the apps script compatibility contract in `backend/services/dashboard_service.py` and update the `POSSIBLE_COLS` map to match your actual SQL column names.
