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

## Frontend: Vercel

This repo contains a Vercel static build. In Vercel, import the GitHub repo and set:

- Framework Preset: `Other`
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variable: `DASHBOARD_API_BASE`

For a frontend that runs on the same PC as the backend, use:

```text
DASHBOARD_API_BASE=http://127.0.0.1:8000
```

If the backend is hosted on a public server, use that public backend URL instead.

When using a Vercel URL with the local backend, allow the frontend origin in `.env` or use:

```text
API_CORS_ORIGINS=*
```
