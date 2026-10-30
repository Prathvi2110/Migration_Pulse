# Migration Pulse AI

Migration Pulse AI is a full-stack college hackathon prototype that turns **live public web development signals** into an explainable, regional Migration Pulse Score. It is designed for aggregate planning conversations: it does not identify individuals, predict exact migration, or claim scientific validation.

## What is included

- React + TypeScript + Vite frontend
- FastAPI backend
- SQLite persistence
- TinyFish Search integration for live public-web evidence
- Evidence Explorer with source links
- Weighted category scoring
- Migration shock simulator
- Analysis history
- API health/config endpoints

## Important: live TinyFish only

This version intentionally has **no demo/fallback evidence mode**. Every saved analysis must come from TinyFish Search. If TinyFish is not configured, the API returns a clear configuration error instead of inventing sample evidence.

TinyFish Search uses the Search API at `https://api.search.tinyfish.ai` and authenticates server-side with the `X-API-Key` header. TinyFish Search returns structured ranked web results, including source URLs and snippets. Search and Fetch are separate TinyFish capabilities; this prototype uses Search for source discovery and traceable evidence.

## Requirements

- Python 3.11+
- Node.js 18+
- A TinyFish API key

## Windows setup

### Terminal 1 — backend

```powershell
cd C:\Users\gopal\Downloads\migrationpulse\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Open `backend\.env` and set:

```env
TINYFISH_API_KEY=your_real_key_here
DEMO_MODE=false
```

Then start FastAPI:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Health check:

`http://127.0.0.1:8001/api/health`

The response must contain:

```json
{"tinyfish_configured": true, "demo_mode": false}
```

### Terminal 2 — frontend

```powershell
cd C:\Users\gopal\Downloads\migrationpulse\frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The Vite proxy sends `/api` requests to FastAPI on port `8001`.

## Troubleshooting

- **TinyFish is not configured:** check `backend\.env`, make sure the variable is exactly `TINYFISH_API_KEY=...`, save the file, and restart FastAPI.
- **Port 8001 is already in use:** do not start a second FastAPI process. Use the existing server, or stop the old process before restarting.
- **Frontend reaches the wrong backend:** confirm `frontend/vite.config.ts` points `/api` to `http://127.0.0.1:8001`.
- **TinyFish returns an HTTP error:** the API now exposes the HTTP status and response body in the `/api/analyze` error so the request can be diagnosed without hiding the provider's response.
- **No usable evidence:** use a more specific region name or a longer lookback period. The application does not fabricate fallback evidence.

## API

- `GET /api/health`
- `GET /api/config/status`
- `POST /api/analyze`
- `GET /api/analysis/{analysis_id}`
- `GET /api/analysis-history`
- `GET /api/evidence/{analysis_id}`
- `POST /api/simulate`
