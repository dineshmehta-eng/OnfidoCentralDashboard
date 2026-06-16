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

## Frontend: Vercel

This repo contains a Vercel static build. In Vercel, import the GitHub repo and set:

- Framework Preset: `Other`
- Build Command: `echo Static frontend ready`
- Output Directory: `frontend`
- Install Command: `echo No install needed`

When using a Vercel URL with the local backend, allow the frontend origin in `.env`. The simplest local setting is:

```text
API_CORS_ORIGINS=*
```

The frontend defaults to:

```text
http://127.0.0.1:8000
```

when it is opened from Vercel.

Because `127.0.0.1` always means the current computer, the Vercel frontend only works on another computer if that computer also has the backend running locally, or if `DASHBOARD_API_BASE` is configured to a public backend URL.
