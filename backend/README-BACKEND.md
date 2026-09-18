# KAVACH AI - Backend

Sovereign On-Premise Agentic AI Workbench - Python/FastAPI backend for the
Smart India Hackathon 2026 prototype.

**Runs fully offline. No cloud AI APIs.** All inference is mock/deterministic
local logic behind real provider interfaces. Default mode is `airgapped`.

---

## 1. Install

From the `backend/` directory:

```bash
# Core (required) — the app starts with just these:
pip install fastapi "uvicorn[standard]" python-multipart pydantic

# Recommended optional (pure-python-ish, offline friendly):
pip install fpdf2 Pillow

# Optional richer deliverables (guarded; skip if offline install fails):
pip install python-docx openpyxl reportlab

# --- or everything at once (optional heavy deps commented out in file): ---
pip install -r requirements.txt
```

Every optional dependency is wrapped in `try/except`. If any are missing the app
still starts and degrades gracefully (e.g. PDFs/DOCX/XLSX are skipped, RAG falls
back to a pure-python hash embedding).

## 2. Generate demo data (once)

From the **repo root** (`26117/`):

```bash
python demo-data/generate_demo_data.py
```

Produces under `demo-data/`: `inspection_report.pdf`, `equipment_manual.pdf`,
`engineering_calculation.pdf` (or `.txt` fallbacks if fpdf2 is absent),
`plant_pid.png` (or `.txt` if Pillow is absent), and `sample_internal_code.py`.
All content is **fictional** (imaginary "KAVACH DEMO REFINERY").

## 3. Run the server

From the `backend/` directory:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The SQLite DB (`backend/kavach.db`) is auto-created and seeded on first startup.
API docs at http://localhost:8000/docs. CORS is enabled for
`http://localhost:3000` and `http://localhost:3001`.

## 4. Configuration

Copy `.env.example` and adjust as needed. Key variables:

| Variable              | Default      | Purpose                              |
|-----------------------|--------------|--------------------------------------|
| `KAVACH_MODE`         | `airgapped`  | `airgapped` blocks external providers|
| `KAVACH_DB`           | `./kavach.db`| SQLite path                          |
| `KAVACH_MAX_UPLOAD_MB`| `25`         | Upload size cap                      |

---

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/api/health` | status/mode/version |
| GET  | `/api/system/status` | GPU/models/vector-db/ocr/sandbox/network |
| POST | `/api/documents/upload` | multipart upload (validated, path-safe) |
| GET  | `/api/documents` | list documents |
| GET  | `/api/documents/{id}` | document detail |
| POST | `/api/tasks` | create task + run agent pipeline |
| GET  | `/api/tasks/{task_id}` | task + run |
| POST | `/api/demo/run` | run the full judge scenario |
| GET  | `/api/demo/stream` | SSE stream of pipeline steps |
| GET  | `/api/agents/runs` | list runs |
| GET  | `/api/agents/runs/{run_id}` | full trace (steps/findings/evidence) |
| GET  | `/api/models` | models + routing rules + providers |
| GET  | `/api/knowledge` | KB stats + sources + sample chunks |
| GET  | `/api/audit-logs` | audit entries |
| POST | `/api/review/{finding_id}/approve` | approve a finding |
| POST | `/api/review/{finding_id}/reject` | reject a finding |
| GET  | `/api/deliverables` | list generated deliverables |
| GET  | `/api/deliverables/{id}/download` | download a deliverable file |

---

## Architecture

```
app/
  main.py            FastAPI app, CORS, middleware, lifespan (init+seed)
  config.py          env-driven config, paths, policies
  api/routes.py      all HTTP routes
  agents/            security, router, document, vision, knowledge,
                     reasoning, verification, deliverable + orchestrator
  models/            provider abstraction (Mock/Ollama/vLLM) + deterministic router
  rag/               chunk + embed (hash fallback) + cosine + KnowledgeBase
  security/          airgap guard, upload validation, mock sandbox, middleware
  services/          scenario content, knowledge KB, deliverables, seed, system status
  database/          sqlite3 layer + schema
  schemas/           pydantic request/response models
```

**Pipeline:** Security -> Router(+Planner) -> Document -> Vision -> Knowledge ->
Reasoning -> Verification -> Deliverable. Each step is persisted with timestamps
and a human-readable message.

**Model router (deterministic):** task text -> task_type -> model
(Qwen3-4B / Vision Model / Code Model / Small Fast Model) with a reason string.

**Security:** airgapped mode blocks external cloud providers; uploads are
extension-allowlisted (`pdf,png,jpg,jpeg,txt,docx,csv,py`), size-capped (25 MB)
and filename-sanitized (path-traversal safe, no werkzeug). Every mutating action
is written to `audit_logs`. A mock sandbox returns `ISOLATED` (no real exec).

**Deliverables** are written to `../generated/`. `.txt` and `.md` are always
produced; `.docx`/`.xlsx`/`.pdf` are added when the relevant library is present.
