## Smart Classroom & Timetable Scheduler (MVP)

This MVP includes:
- FastAPI backend with SQLite, CSV ingest, heuristic scheduler, and REST API
- Minimal frontend (vanilla JS) for CSV upload and timetable visualization
- Docker Compose for one-command local run

### Quick Start (Recommended - Local without Docker)
1. Backend
   - Python 3.10+
   - `cd backend`
   - `python -m venv .venv && .venv/Scripts/activate`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. Frontend (serve over HTTP, not file://)
   - In another terminal: `cd frontend`
   - `python -m http.server 5173` (Python 3) OR `python serve.py`
   - Open `http://127.0.0.1:5173` in your browser
3. In the app Settings, set Backend API URL to `http://127.0.0.1:8000` and click Test Connection.
4. Upload CSVs from `sample_data/`, then click Generate Timetable.

### Quick Start (Docker)
- `docker compose up --build`
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

### API
- `GET /api/health`
- `POST /api/upload` (multipart with `teachers`, `rooms`, `sections`, `courses`)
- `POST /api/generate` (optional body: `{ days: string[], slots: string[] }`)
- `GET /api/timetable`

### CSV Formats
See `sample_data/*.csv` for headers and examples.

### Notes
- Avoid opening `index.html` with `file://`. Serve via HTTP to prevent CORS/network blocking.
- If using VPN/Proxy/Antivirus, allow localhost connections or temporarily disable.

### Embedding / Integration
- Use REST API directly from your site (CORS enabled)
- Embed frontend via iframe pointing to served build

### License
For hackathon/demo use.
