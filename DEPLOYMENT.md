# Deployment

## Backend: Run Locally

```powershell
cd C:\Users\Dineshm\.codex\Onfido_SQL_Dashboard
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/?v=20260614_all_pages_fix_final
```

For another computer on the same network, run the backend on all interfaces:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then open the dashboard using this computer's LAN IP, for example:

```text
http://172.10.11.162:8000/?v=20260614_all_pages_fix_final
```

If another computer cannot open it, allow inbound TCP port `8000` in Windows Firewall.

## Backend: Auto-Start On Windows Login

Run once:

```powershell
cd C:\Users\Dineshm\.codex\Onfido_SQL_Dashboard
powershell -ExecutionPolicy Bypass -File .\scripts\register_backend_autostart.ps1
```

The task name is `OnfidoCentralDashboardBackend`.

To remove it:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\unregister_backend_autostart.ps1
```

## Frontend + Public API: Vercel

This repo contains a Vercel static frontend and a Vercel FastAPI entrypoint in `main.py`.
In Vercel, import the GitHub repo and set:

- Framework Preset: `Other`
- Build Command: leave empty
- Output Directory: leave empty

The public Vercel frontend uses same-origin API calls:

```text
/api/init
/api/dashboard
```

So it can be opened from any system without calling `127.0.0.1`.

## ETM / Task Skip: Hourly SQL Sync

The ETL job syncs these Google worksheets into SQL every hour:

- `DOC ETM` -> `stg_doc_etm`
- `DOC Task Skip` -> `stg_doc_task_skip`
- `POA ETM` -> `stg_poa_etm`

Required local credential:

```text
config/service_account.json
```

Run once manually:

```powershell
cd C:\Users\Dineshm\.codex\Onfido_SQL_Dashboard
powershell -ExecutionPolicy Bypass -File .\scripts\run_etl_once.ps1
```

Register hourly schedule:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_etl_hourly_task.ps1
```
