# Migration Pulse AI backend

Create a virtual environment, install `requirements.txt`, copy `.env.example` to `.env`, then run `uvicorn app.main:app --reload --port 8000`. The interactive API docs are available at `http://127.0.0.1:8000/docs`.

Set `TINYFISH_API_KEY` for live Search API calls. The documented TinyFish header is `X-API-Key`; the backend sends it server-side and never exposes it to the browser. Keep `DEMO_MODE=true` for a credential-free prototype. Demo results are explicitly labelled in API responses and the dashboard.
