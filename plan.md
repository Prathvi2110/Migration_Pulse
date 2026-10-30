# Migration Pulse AI — Implementation Plan

## Approach
Build a beginner-friendly full-stack prototype with a Vite React TypeScript frontend and a FastAPI Python backend. SQLite/SQLAlchemy persist analysis and evidence records. The backend owns validation, TinyFish calls, evidence normalization, scoring, explanations, simulation math, and all live/demo labeling. The frontend is a thin API client with responsive dashboard views and Recharts visualizations.

The TinyFish service will use the documented `X-API-Key` header and Search API endpoint when `TINYFISH_API_KEY` is configured. It will request news results for category-specific regional queries, normalize the returned URLs/titles/snippets, and fail clearly without fabricating live data. A deterministic demo dataset is explicitly labelled when `DEMO_MODE=true`.

## Structure
- `frontend/`: Vite React UI, API client, dashboard components, styles, route manifest.
- `backend/app/`: FastAPI app, SQLAlchemy models, Pydantic schemas, services for TinyFish, evidence processing, scoring, explanations, simulation, and API routes.
- `backend/tests/`: pytest coverage for health, validation, scoring, evidence handling, simulation, persistence, and TinyFish failures.
- `README.md`: Windows-friendly setup and troubleshooting.

## Design
Three candidate styles: Signal-room editorial (0.06); civic data atlas (0.07); midnight operations console (0.08). Chosen: **midnight operations console**.

- **Design movement:** A calm intelligence operations console with layered panels, compact metadata, and an electric signal accent.
- **Core principles:** evidence before assertion; high information density with breathing room; status is always explicit; every action has visible feedback.
- **Color philosophy:** deep navy reduces glare, violet marks analysis, cyan marks infrastructure evidence, and amber flags uncertainty without implying alarm.
- **Layout paradigm:** a persistent left rail anchors navigation while the main canvas uses an asymmetric lead score panel and a right-side evidence stream rather than a uniform card grid.
- **Signature elements:** a pulse-line logo mark, thin luminous dividers, and category chips that behave like instrument readouts.
- **Interaction philosophy:** controls are direct and reversible; live/demo status is never hidden; empty states explain what is missing.
- **Animation:** subtle 180ms panel fades and pulse-line shimmer only on active analysis; no decorative motion during reading.
- **Typography:** Inter/system sans for UI with JetBrains Mono for scores, timestamps, and source metadata.
- **Brand essence:** regional development intelligence for planners and student builders; precise, transparent, grounded.
- **Brand voice:** direct and qualified. Example lines: “Observed signals, not migration certainty.” “Run a regional scan to build the evidence trail.”
- **Wordmark/logo:** a compact three-node pulse line inside a rounded square, followed by the wordmark.
- **Signature brand color:** signal violet `#9B8AFB`.

## Build workflow
Implement backend first, then frontend integration, then run Python tests and frontend production build. Start the preview on port 3000, verify the route manifest and health behavior, and keep credentials in backend `.env` only.
