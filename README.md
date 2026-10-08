<div align="center">

# 🛡️ KAVACH AI

### Sovereign Intelligence. Secured On-Premise.

**A self-hosted, air-gapped, agentic AI workbench for confidential industrial work — built on open-weight multimodal LLMs.**

Smart India Hackathon 2026 · Problem Statement **26117** · Mangalore Refinery and Petrochemicals Limited (MRPL)

</div>

---

> **Prototype notice.** This is a **demonstration prototype** for SIH judges. It runs a complete, visually-observable agentic workflow using a **deterministic mock local-inference layer** so the demo works on any laptop with no GPU and **no internet**. Every expensive AI operation sits behind a real interface (`ModelProvider`, RAG pipeline, agents) so a real local model server (Ollama / llama.cpp / vLLM) can be dropped in without changing the application above it. We do **not** claim a model actually performed inference where mock data is used.

---

## 1 · The Problem

Refineries, PSUs, defence-linked manufacturers and government offices generate huge volumes of **confidential** knowledge work — P&IDs, inspection reports, engineering calculations, internal code, vendor negotiations, unreleased designs. This data **cannot** be sent to public cloud AI (Claude, ChatGPT, Gemini, Codex). So teams are stuck with two bad options:

1. **Do it manually** — slow, inconsistent.
2. **Paste confidential material into public tools** — a data-sovereignty and security breach.

## 2 · The Solution

KAVACH AI is a **sovereign AI appliance** that stays inside the organisation's network. It routes each task to the **right local agent + right local model + right local tools**, retrieves evidence from a **local knowledge base**, **verifies** every finding against its source, and produces **professional deliverables** — with a **human-in-the-loop** approval gate. **Zero bytes leave the environment.**

The differentiator is not "a chatbot on-prem". It is an **agentic industrial workbench** where the security, routing, planning, analysis, retrieval, reasoning, verification and delivery steps are all **visible and auditable**.

### What the judges see (WOW moments)

| # | Moment | Where |
|---|--------|-------|
| 1 | Air-gapped security dashboard & data-boundary diagram | Overview · Security Center |
| 2 | Live multi-agent execution trace | Workbench |
| 3 | Intelligent model routing (right task → right model) | Model Router |
| 4 | Multimodal P&ID region analysis | Workbench / Vision |
| 5 | Evidence-backed answers (source · page · excerpt · relevance) | everywhere |
| 6 | Verification layer (94% · 8/9 evidence-backed) | Workbench |
| 7 | Professional deliverable generation (PDF/DOCX/XLSX) | Deliverables |
| 8 | Human-in-the-loop approval ("AI recommends, engineer approves") | Report view |

## 3 · Architecture

```
                        USER (engineer request)
                                 │
                        ┌────────▼─────────┐
                        │  SECURITY AGENT   │  policy + classification, airgap guard
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │   ROUTER AGENT    │  task classification
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │     PLANNER       │  builds execution plan
                        └────────┬─────────┘
        ┌───────────────────────┼───────────────────────┐
┌───────▼───────┐      ┌────────▼────────┐      ┌────────▼────────┐
│ DOCUMENT AGENT │      │  VISION AGENT   │      │ KNOWLEDGE AGENT │
│  OCR / extract │      │ P&ID / diagram  │      │  RAG retrieval  │
└───────┬───────┘      └────────┬────────┘      └────────┬────────┘
        └───────────────────────┼───────────────────────┘
                        ┌────────▼─────────┐
                        │ REASONING AGENT   │  combine evidence → findings
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │VERIFICATION AGENT │  cross-check findings vs evidence
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │   HUMAN REVIEW    │  approve / edit / reject
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │ DELIVERABLE AGENT │  PDF / DOCX / XLSX / report
                        └──────────────────┘

   All of the above runs INSIDE the organisation network. 🚫 Internet / Cloud AI is blocked.
```

**Model Router** picks a local model per task type:
`Vision` (P&ID/images) · `Qwen3-4B` (reasoning) · `Code` (source code) · `Phi-3-mini` (fast classification/extraction) · `bge-large-en` (embeddings).

### Tech stack

| Layer | Choice |
|-------|--------|
| Frontend | Next.js 14 · React 18 · TypeScript · Tailwind CSS · Recharts · zustand |
| Backend | Python · FastAPI · SQLite |
| RAG | chunk → hash-embed → cosine similarity (pure-python fallback; ChromaDB-ready) |
| OCR / PDF | Tesseract abstraction · PyMuPDF/fpdf2 (import-guarded) |
| Inference | `MockLocalModelProvider` (drop-in Ollama / vLLM adapters) |
| Packaging | Docker · Docker Compose |

### Repository layout

```
kavach-ai/
├── frontend/            Next.js app (9 console sections)
│   ├── app/             overview, workbench, vault, knowledge, runs, router, security, deliverables, system
│   ├── components/      shell (sidebar/topbar) · ui primitives · viz (boundary, timeline, P&ID, findings…)
│   └── lib/             types · deterministic demo dataset · zustand store · optional API client
├── backend/             FastAPI service
│   └── app/             api · agents (8) · models (providers + router) · rag · security · services · database · schemas
├── demo-data/           fictional P&ID PNG + inspection/manual/calc PDFs + sample code
├── generated/           produced deliverables (PDF/DOCX/XLSX/TXT/MD)
├── docker/              backend + frontend Dockerfiles
├── docker-compose.yml
└── .env.example
```

## 4 · Setup

### Option A — Docker (one command)

```bash
docker compose up --build
# frontend → http://localhost:3000
# backend  → http://localhost:8000/api/health
```

### Option B — Local (Windows / macOS / Linux)

**Frontend** (Node 18+):
```bash
cd frontend
npm install
npm run build      # verifies a clean production build
npm run dev        # → http://localhost:3000
```

**Backend** (Python 3.10+), in a second terminal:
```bash
cd backend
pip install -r requirements.txt
# (once) regenerate demo data:  python ../demo-data/generate_demo_data.py
python -m uvicorn app.main:app --reload --port 8000   # → http://localhost:8000
```

> The frontend runs **standalone** on its baked demo dataset — it does **not** require the backend to be up. When the backend **is** running, the **System** page shows `FastAPI Backend Connected` and the same contract can drive the UI live.

## 5 · Demo Instructions (5-minute judge flow)

1. **Overview** — "Industrial orgs can't send confidential data to cloud AI." Point to **External Data Transfers: 0** and the **Data Boundary** diagram (cloud link severed).
2. Click **▶ Start Judge Demo** (top-right) — it launches the full scenario and jumps to the Workbench.
3. **Workbench** — watch the agent pipeline execute live: `Security → Router → Model Router → Planner → Document → Vision → Knowledge → Reasoning → Verification → Deliverable`, with a streaming inference console.
4. **Model Router** — "KAVACH doesn't send every task to one model." Click task types to see the routing decision + reason.
5. **Evidence** — open any finding → source · page · excerpt · relevance · verification status.
6. **Security Center** — air-gapped, external API blocked, audit log, `0 external transmissions`.
7. **Deliverables** — open the **Engineering Review Report**; show verification stats and evidence.
8. **Human Review** — "AI recommends. Engineer approves." Approve / edit / reject a flagged finding.

The demo is **deterministic** and needs **no internet**.

## 6 · Agentic Planner Workflow

Alongside the fixed judge-demo pipeline (unchanged, still fully deterministic) the backend has a small, **bounded agentic loop**: `POST /api/agent/run`.

```
SecurityAgent ─► PlannerAgent ──► pick next action ──► allowlisted tool ──┐
                      ▲                                                   │
                      └──────────── updated run state ◄───────────────────┘
        stops on: finish · max steps · repeated action · rejected tool call
```

- **`PlannerAgent`** (`backend/app/agents/planner_agent.py`) chooses one action per step: `search_knowledge`, `inspect_document`, `analyze_pid`, `reason`, `verify`, `human_review` or `finish`. Eligible actions are derived from run state, so prerequisites cannot be skipped. For example, P&ID analysis is only planned when the task mentions a diagram.
- **Bounded loop** — `max_steps` (default 10, hard cap 20, `KAVACH_PLANNER_MAX_STEPS`). Repeating an identical action is treated as a loop and stops the run. Any stop other than `finish` marks the run `halted` and escalates every finding to human review.
- **Allowlisted tool registry** (`backend/app/agents/tools.py`) — a fixed, read-only set of six tools that wrap the existing agents and the local RAG index. There is no dynamic registration and **no shell, SQL, filesystem or network/cloud tool**. Unknown tool names and unexpected arguments are rejected. `GET /api/agent/tools` lists the allowlist.
- **Human approval gate** (`backend/app/agents/review_gate.py`) — a finding is held for approval when it is high/critical severity, cites no evidence or a source that is not in the knowledge base, is below `KAVACH_REVIEW_MIN_CONFIDENCE` (default 75), or was never verified. The gate is re-applied when the loop ends, regardless of what the planner did. Such runs end as `awaiting_review` and become `completed` once every flagged finding has been approved or rejected through `/api/review/{id}/approve|reject`.

```bash
curl -X POST localhost:8000/api/agent/run -H 'Content-Type: application/json' \
     -d '{"task": "Inspect Unit 4 P&ID and inspection report for corrosion", "max_steps": 10}'
```

The response is the normal run trace plus a `planner` block (`trace`, `stop_reason`, `steps_used`, `review_required`).

**Live knowledge search.** `POST /api/knowledge/search` (`{"query": "...", "top_k": 4}`) queries the existing RAG `KnowledgeBase`. The **Knowledge Base** page calls it and shows a `Live backend` badge; if the backend is unreachable it shows a notice and falls back to the baked demo dataset (`Demo fallback`), so the page works offline.

### Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests -q
```

### Limitations

- The planner's tools wrap the prototype's deterministic agents, so findings still come from the fictional scenario dataset, not from real model inference over the task text.
- Agentic runs do not generate deliverable files; use the demo pipeline for reports.
- The planner trace is returned in the response and stored as run steps; review reasons are not stored in their own database column.
- The demo knowledge base is small (a handful of chunks) and uses hash embeddings unless `sentence-transformers` is installed, so similarity scores are low in absolute terms.
- The Ollama adapter is covered only by its airgap guard test; it has not been exercised against a running Ollama server.

## 6a · Local Model Integration (replacing the mock)

All inference goes through `BaseModelProvider` (`backend/app/models/providers.py`): `generate`, `embed`, `health`.

`MockLocalModelProvider` is the default and needs no network. Optional local Ollama support:

```bash
ollama serve && ollama pull qwen3:4b
export KAVACH_INFERENCE_PROVIDER=ollama      # default: mock
export OLLAMA_BASE_URL=http://localhost:11434 OLLAMA_MODEL=qwen3:4b
```

- In `airgapped` mode the Ollama URL **must be loopback** (`localhost` / `127.0.0.1`); anything else raises `AirgapViolation`.
- With Ollama enabled, the planner may ask the model to pick among the *eligible* actions only; an unclear answer or an unreachable server falls back to the deterministic choice / mock provider.
- `VLLMProvider` remains a stub.

For real embeddings/vector search, install `chromadb` + `sentence-transformers` (import-guarded; the pure-python hash-embedding fallback is used otherwise).

## 7 · Security Architecture

- **`KAVACH_MODE=airgapped`** (default): external model providers and URLs are disabled; only local inference is permitted. An **airgap guard** rejects any external provider request.
- **No cloud AI SDKs** — no OpenAI / Anthropic / Gemini / Azure / Bedrock. The app makes no outbound AI calls.
- **Data residency** — documents, embeddings, runs and deliverables never leave the host filesystem / SQLite.
- **Upload controls** — file-type allowlist, 25 MB size cap, filename sanitisation (path-traversal safe), input validation.
- **Sandbox abstraction** — uploaded code is **never executed on the host**; the sandbox executor returns an isolated result (`STATUS: ISOLATED`), ready to back with gVisor/Docker.
- **RBAC + audit log** — every action (upload, OCR, index, route, retrieve, verify, generate) is written to a local, tamper-evident audit log surfaced in the Security Center.
- **Docker air-gap** — the backend container runs with no route to the public internet.

## 8 · Future Roadmap

- Swap mock provider for on-GPU **vLLM** serving Qwen3 + Qwen2-VL + a code model, with dynamic batching.
- Real **ChromaDB** vector store + `bge-large-en` embeddings and hybrid (BM25 + dense) retrieval.
- Fine-grained **RBAC** with SSO/LDAP and per-classification access policies.
- True **P&ID computer vision** (symbol detection + tag OCR) replacing the deterministic region mock.
- Deliverable templating engine (approval notes, board decks, Excel models) with org branding.
- Hardware appliance packaging (signed image, secure boot, attestation) for turnkey on-prem deployment.
- Full audit export (WORM storage) and compliance reporting.

---

<div align="center">
<sub>KAVACH AI · open-weight local models · no data leaves the site. Built for SIH 2026 · PS 26117 · MRPL.</sub>
</div>
