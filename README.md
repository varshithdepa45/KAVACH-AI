<div align="center">

# 🛡️ KAVACH AI

### Sovereign Intelligence. Secured On-Premise.

**A self-hosted, air-gapped, agentic AI workbench for confidential industrial work.**

Smart India Hackathon 2026 · Problem Statement **26117** · Mangalore Refinery and Petrochemicals Limited (MRPL)

</div>

---

> **Prototype notice — what is real and what is mocked.**
> This is a demonstration prototype. The **agent architecture, the agentic planner loop, the tool allowlist, the human-approval gate, the RAG index, document upload and the audit log are real, running code.** The **model inference is mocked** by default: a deterministic `MockLocalModelProvider` stands in for the LLM so the demo runs on any laptop with no GPU and no internet. The judge-demo findings are a fixed, **fictional** dataset. Findings for *uploaded* documents are produced by local keyword extraction, not by a language model. Each section below says which is which.

---

## Contents

1. [The problem](#1--the-problem)
2. [The solution](#2--the-solution)
3. [The agents](#3--the-agents)
4. [How agentic AI is used](#4--how-agentic-ai-is-used)
5. [The three ways to run it](#5--the-three-ways-to-run-it)
6. [Architecture and tech stack](#6--architecture-and-tech-stack)
7. [Setup](#7--setup)
8. [Demo walkthrough](#8--demo-walkthrough)
9. [API reference](#9--api-reference)
10. [Local model integration](#10--local-model-integration)
11. [Security](#11--security)
12. [Tests](#12--tests)
13. [Limitations](#13--limitations)
14. [Roadmap](#14--roadmap)

---

## 1 · The problem

Refineries, PSUs, defence-linked manufacturers and government offices produce large volumes of **confidential** knowledge work: P&IDs, inspection reports, engineering calculations, internal code, vendor negotiations. This data **cannot** be sent to a public cloud AI service, which leaves two bad options:

1. **Do the work manually** — slow and inconsistent.
2. **Paste confidential material into public tools** — a data-sovereignty breach.

## 2 · The solution

KAVACH AI is designed as an AI appliance that stays inside the organisation's network. A request is handled by a team of small, single-purpose **agents**: one checks the security policy, one picks the right local model, others read documents, retrieve evidence, reason over it, verify the result and write the report. A **human engineer approves** anything risky before it counts as done.

The point is not "a chatbot on-prem". It is a workbench where every step — security, routing, planning, retrieval, reasoning, verification, approval — is **visible and auditable**.

---

## 3 · The agents

There are **nine agents**, plus two supporting components (the tool registry and the review gate). All live in `backend/app/agents/`. Every agent reads and writes one shared `RunContext` and records what it did as a step, so a run leaves a complete trace.

| # | Agent | File | What it does | Real or mocked? |
|---|-------|------|--------------|-----------------|
| 1 | **Security Agent** | `security_agent.py` | First gate of every run. Confirms the mode (`airgapped`), checks that the active model provider is local, and refuses to continue if it is an external/cloud provider. | **Real** check. |
| 2 | **Router Agent** | `router_agent.py` | Classifies the task (vision / code / extraction / classification / reasoning) and selects the matching local model. In the fixed pipeline it also records the execution plan. | **Real** keyword-based classifier. The models it routes to are mocked. |
| 3 | **Document Agent** | `document_agent.py` | Loads the documents for the run. For an uploaded file it reports the text extracted locally from that file. | **Real** text extraction for TXT / CSV / PY / DOCX / PDF. The demo scenario's "OCR" step is mocked. |
| 4 | **Vision Agent** | `vision_agent.py` | Detects equipment regions on the P&ID diagram. | **Mocked** — returns fixed regions for the demo P&ID. It is skipped for uploaded documents, because no vision model is loaded. |
| 5 | **Knowledge Agent** | `knowledge_agent.py` | Retrieval (RAG). Searches the local vector index for passages relevant to the task. For an uploaded document it indexes that document's text for the run. | **Real** chunk → embed → cosine-similarity search. Embeddings are hash-based unless `sentence-transformers` is installed. |
| 6 | **Reasoning Agent** | `reasoning_agent.py` | Turns the gathered evidence into findings, each with severity, confidence and cited evidence. | Demo scenario: **fixed fictional findings**. Uploaded document: **real extraction** of sentences that match a risk-term list (no LLM). |
| 7 | **Verification Agent** | `verification_agent.py` | Cross-checks findings against their evidence and flags what needs a human. | Uploaded document: **real** — every quoted excerpt is re-checked against the file. Demo scenario: fixed score (94%). |
| 8 | **Deliverable Agent** | `deliverable_agent.py` | Writes the report files: TXT and Markdown always; DOCX, XLSX and PDF when the libraries are installed. | **Real** files, written to `generated/`. |
| 9 | **Planner Agent** | `planner_agent.py` | The agentic one. Looks at the current state of the run and **decides which action to take next**, step by step, until the work is done. | **Real** loop. The choice is rule-based with the mock provider; a local LLM can make it when Ollama is enabled. |

**Supporting components**

| Component | File | Role |
|-----------|------|------|
| **Orchestrator** | `orchestrator.py` | Runs agents 1–8 in a fixed order and saves the trace, findings, evidence and deliverables to SQLite. |
| **Tool registry** | `tools.py` | The fixed, read-only list of six tools the Planner Agent is allowed to call. |
| **Review gate** | `review_gate.py` | Decides which findings a human must approve. This is the human-in-the-loop step. |

---

## 4 · How agentic AI is used

### A fixed pipeline is not agentic

Agents 1–8 can run as a **pipeline**: the orchestrator calls them in the same order every time. That is automation — useful and predictable, but nothing in it makes a decision about what to do next.

### The agentic loop

`POST /api/agent/run` is different. No order is hard-coded. The **Planner Agent** is asked, repeatedly, *"given what we know so far, what should happen next?"* It picks one action, a tool carries it out, the run state is updated, and the planner is asked again.

```
                ┌──────────────────────────────────────────────────┐
                │                 RUN STATE                        │
                │  task · documents · retrieved evidence ·         │
                │  findings · verification · review status         │
                └───────────┬──────────────────────▲───────────────┘
                            │ observe              │ update
                   ┌────────▼─────────┐   ┌────────┴─────────┐
 Security Agent ─► │  PLANNER AGENT   │──►│  ALLOWLISTED     │
 (runs once first) │  choose 1 action │   │  TOOL executes   │
                   └────────┬─────────┘   └──────────────────┘
                            │
              stops on: finish · step limit · repeated action · rejected tool
                            │
                   ┌────────▼─────────┐
                   │   REVIEW GATE    │  always applied, whatever the planner did
                   └────────┬─────────┘
              completed  /  awaiting_review  /  halted
```

**Observe → decide → act → repeat** is what makes it agentic:

- **It decides from state, not from a script.** The planner computes which actions are *eligible* right now. Documents not loaded? `inspect_document` is eligible. Findings exist but are unverified? Only `verify` is eligible.
- **The path depends on the task.** A task that mentions a P&ID or diagram gets an `analyze_pid` step; a text-only task skips it. Two different requests produce two different traces.
- **It uses tools.** The planner cannot touch data itself. Each action maps to one tool, and the tools wrap the other agents.

### The actions the planner can choose

| Action | Tool does | Eligible when |
|--------|-----------|---------------|
| `inspect_document` | Runs the Document Agent | Documents are not loaded yet |
| `analyze_pid` | Runs the Vision Agent | The task mentions a diagram and regions are not analysed |
| `search_knowledge` | Searches the local RAG index with the task text | Nothing has been retrieved yet |
| `reason` | Runs the Reasoning Agent | Evidence has been gathered and there are no findings |
| `verify` | Runs the Verification Agent, then the review gate | Findings exist but are not verified |
| `human_review` | Holds flagged findings for an engineer | Verification says approval is required |
| `finish` | Ends the run | Everything above is complete |

### Guardrails — why the loop is safe to run

An agent that picks its own actions needs hard limits. These are enforced in code, outside the planner, and covered by tests:

1. **Bounded steps.** At most `max_steps` decisions per run (default 10, hard cap 20). Hitting the limit halts the run.
2. **Loop detection.** Choosing the exact same action with the same arguments twice halts the run.
3. **Tool allowlist.** Only the six tools above exist. There is no dynamic registration and **no shell, SQL, filesystem or network tool**. An unknown tool name or an unexpected argument is rejected and halts the run.
4. **Prerequisites cannot be skipped.** Eligibility is computed from the run state, so the planner cannot reason before gathering evidence or finish before verifying.
5. **The review gate always runs last**, independently of the planner. Even a planner that tried to finish early cannot release an unreviewed finding.
6. **Fail safe.** Any stop other than `finish` marks the run `halted` and escalates **every** finding to human review.

### Human-in-the-loop

The review gate holds a finding for engineer approval when any of these is true:

- its severity is **high** or **critical**;
- it cites **no evidence**, or a source that is **not in the knowledge base**;
- its confidence is below the threshold (`KAVACH_REVIEW_MIN_CONFIDENCE`, default 75);
- it was **never verified**.

A run with held findings ends as `awaiting_review` and becomes `completed` only after an engineer approves or rejects each one (`POST /api/review/{id}/approve|reject`, or the buttons on the **Agent Runs** page). *AI recommends; the engineer approves.*

### Where the LLM fits

With the default mock provider, when several actions are eligible the planner takes the first — so runs are deterministic and repeatable. With a local **Ollama** model enabled, the planner asks the model to choose **among the eligible actions only**. An unclear answer, or an unreachable server, falls back to the deterministic choice. The model gets to make the judgement call; it never gets to leave the guardrails.

---

## 5 · The three ways to run it

| Mode | Endpoint | Who decides the order | Where findings come from |
|------|----------|----------------------|--------------------------|
| **Demo pipeline** | `POST /api/demo/run` | Orchestrator (fixed) | Fixed fictional "KAVACH DEMO REFINERY" scenario |
| **Document analysis** | `POST /api/documents/{id}/analyze` | Orchestrator (fixed) | The uploaded file's own text, by risk-term extraction |
| **Agentic planner** | `POST /api/agent/run` | **Planner Agent** | Fixed fictional scenario (the tools wrap the demo agents) |

```bash
# Agentic run
curl -X POST localhost:8000/api/agent/run -H 'Content-Type: application/json' \
     -d '{"task": "Inspect Unit 4 P&ID and inspection report for corrosion", "max_steps": 10}'
```

The response is the full run trace plus a `planner` block: the `trace` of decisions (action, reason, status), `stop_reason`, `steps_used` and `review_required`.

**In the UI**

- **Workbench → Run KAVACH** plays the judge demo as a client-side animation over baked data. It works with the backend switched off.
- **Workbench → Run agentic planner** calls the backend planner with the task you typed and shows its decision trace.
- **Workbench / Document Vault → Analyze document** runs document analysis on a stored file.
- **Agent Runs** lists the backend's runs with their trace, findings and evidence, and has the **Approve / Reject** buttons.

---

## 6 · Architecture and tech stack

```
                        USER (engineer request)
                                 │
                        ┌────────▼─────────┐
                        │  SECURITY AGENT   │  mode + provider check
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │   ROUTER AGENT    │  task type → local model
                        └────────┬─────────┘
        ┌───────────────────────┼───────────────────────┐
┌───────▼───────┐      ┌────────▼────────┐      ┌────────▼────────┐
│ DOCUMENT AGENT │      │  VISION AGENT   │      │ KNOWLEDGE AGENT │
│ text extraction│      │ P&ID regions    │      │  RAG retrieval  │
└───────┬───────┘      └────────┬────────┘      └────────┬────────┘
        └───────────────────────┼───────────────────────┘
                        ┌────────▼─────────┐
                        │ REASONING AGENT   │  evidence → findings
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │VERIFICATION AGENT │  findings vs evidence
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │   HUMAN REVIEW    │  approve / reject
                        └────────┬─────────┘
                        ┌────────▼─────────┐
                        │ DELIVERABLE AGENT │  TXT / MD / DOCX / XLSX / PDF
                        └──────────────────┘

  Fixed pipeline: the orchestrator walks this top to bottom.
  Agentic run:    the PLANNER AGENT chooses which box runs next.
```

| Layer | Choice |
|-------|--------|
| Frontend | Next.js 14 · React 18 · TypeScript · Tailwind CSS · Recharts · zustand |
| Backend | Python 3.10+ · FastAPI · SQLite (stdlib `sqlite3`) |
| RAG | chunk → embed → cosine similarity, in memory. Hash embeddings by default; `sentence-transformers` if installed |
| Text extraction | `pypdf` (PDF) · `python-docx` (DOCX) · plain read (TXT / CSV / PY) |
| Inference | `MockLocalModelProvider` (default) · optional local Ollama adapter |
| Packaging | Docker · Docker Compose |

```
kavach-ai/
├── frontend/            Next.js console (9 sections)
│   ├── app/             overview, workbench, vault, knowledge, runs, router, security, deliverables, system
│   ├── components/      shell · ui primitives · viz (timeline, P&ID, findings, live runs…)
│   └── lib/             types · baked demo dataset · zustand store · backend API client
├── backend/
│   ├── app/
│   │   ├── agents/      the 9 agents · orchestrator · tools · review_gate
│   │   ├── models/      provider abstraction (mock / Ollama / vLLM stub) · model router
│   │   ├── rag/         chunking, embeddings, KnowledgeBase
│   │   ├── security/    airgap guard · upload validation · audit middleware · sandbox stub
│   │   ├── services/    scenario data · document analysis · deliverables · seed · system status
│   │   ├── api/         HTTP routes
│   │   ├── database/    SQLite schema + helpers
│   │   └── schemas/     request/response models
│   └── tests/           pytest suite
├── demo-data/           fictional P&ID, inspection report, manual, calculation, sample code
├── generated/           sample generated reports
├── docker/              backend + frontend Dockerfiles
└── docker-compose.yml
```

The **Model Router** maps a task type to a local model. The model names differ between the two halves of the prototype because both are placeholders: the backend catalogue lists `Qwen3-4B`, `Vision Model`, `Code Model` and `Small Fast Model`; the frontend's baked dataset shows `Qwen3-4B`, `Qwen2-VL-7B`, `DeepSeek-Coder-6.7B`, `Phi-3-mini` and `bge-large-en`. None of these models is actually loaded.

---

## 7 · Setup

### Option A — Docker

```bash
docker compose up --build
# frontend → http://localhost:3000
# backend  → http://localhost:8000/api/health
```

### Option B — Local (Windows / macOS / Linux)

**Backend** (Python 3.10+):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000   # → http://localhost:8000/docs
```

**Frontend** (Node 18+), in a second terminal:

```bash
cd frontend
npm install
npm run dev        # → http://localhost:3000
```

The frontend also runs **on its own**: with the backend off it shows its baked demo dataset, and the features that need the backend (document analysis, agentic planner, live runs, live knowledge search) are disabled or fall back with a notice.

Configuration is by environment variable — see `.env.example`. The defaults keep everything local.

---

## 8 · Demo walkthrough

1. **Overview** — the problem, **External Data Transfers: 0**, and the data-boundary diagram.
2. Click **▶ Start Judge Demo** — launches the scenario and opens the Workbench.
3. **Workbench** — watch the pipeline: `Security → Router → Model Router → Planner → Document → Vision → Knowledge → Reasoning → Verification → Deliverable`.
4. **Workbench → Run agentic planner** *(backend running)* — the Planner Agent's decisions appear one by one, ending in `awaiting review`.
5. **Agent Runs** — open that run, read each finding's evidence, and **Approve / Reject** the held findings. The run flips to `completed`.
6. **Document Vault** — upload a text, DOCX or PDF file and click **Analyze document**. The findings quote the file you uploaded.
7. **Knowledge Base** — live search against the local RAG index (`Live backend` badge).
8. **Model Router**, **Security Center**, **Deliverables**, **System** — routing rules, audit log, generated reports, service status.

---

## 9 · API reference

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Status, mode, version |
| GET | `/api/system/status` | Models, vector DB, sandbox, network (GPU figures are simulated) |
| POST | `/api/documents/upload` | Upload a file (type allowlist, 25 MB cap, sanitised name) |
| GET | `/api/documents` · `/api/documents/{id}` | List / fetch documents |
| POST | `/api/documents/{id}/analyze` | Run the pipeline on one stored document |
| POST | `/api/tasks` | Create a task and run the demo pipeline |
| POST | `/api/demo/run` | Run the demo pipeline |
| GET | `/api/demo/stream` | Demo pipeline steps as server-sent events |
| GET | `/api/agent/tools` | The planner's tool allowlist |
| POST | `/api/agent/run` | **Bounded agentic planner run** (`task`, optional `max_steps`) |
| GET | `/api/agents/runs` · `/api/agents/runs/{id}` | Run list / full trace |
| POST | `/api/review/{finding_id}/approve` · `/reject` | Human review decision |
| GET | `/api/models` | Model catalogue, routing rules, providers |
| GET | `/api/knowledge` | Knowledge-base stats |
| POST | `/api/knowledge/search` | RAG search (`query`, `top_k` 1–10) |
| GET | `/api/audit-logs` | Audit entries |
| GET | `/api/deliverables` · `/api/deliverables/{id}/download` | List / download reports |

Interactive docs: `http://localhost:8000/docs`.

---

## 10 · Local model integration

All inference goes through `BaseModelProvider` (`backend/app/models/providers.py`): `generate`, `embed`, `health`. The mock is the default and needs no network. To use a local Ollama server instead:

```bash
ollama serve && ollama pull qwen3:4b
export KAVACH_INFERENCE_PROVIDER=ollama      # default: mock
export OLLAMA_BASE_URL=http://localhost:11434 OLLAMA_MODEL=qwen3:4b
```

- In `airgapped` mode the Ollama URL **must be loopback** (`localhost` / `127.0.0.1`); anything else raises `AirgapViolation`.
- With Ollama enabled, the Planner Agent asks the model to choose among the eligible actions. If the server is down the run continues on the mock provider.
- `VLLMProvider` is a stub.

For real embeddings, install `sentence-transformers` (import-guarded; the hash-embedding fallback is used otherwise).

---

## 11 · Security

**Implemented**

- **Airgapped mode** (`KAVACH_MODE=airgapped`, the default). The Security Agent and the airgap guard reject external providers, and any inference URL that is not loopback.
- **No cloud AI SDKs.** The backend has no OpenAI / Anthropic / Gemini / Azure / Bedrock dependency and makes no outbound AI call.
- **Local storage only.** Documents, the index, runs and reports stay on the host filesystem and in SQLite.
- **Upload controls.** File-type allowlist, 25 MB size cap, filename sanitisation that is safe against path traversal; an upload never overwrites an earlier file.
- **Uploaded code is never executed.** The sandbox component is a stub that performs no execution.
- **Planner guardrails.** Tool allowlist, step limit, loop detection and the review gate (section 4).
- **Audit log.** Uploads, analyses, runs, searches, reviews and downloads are written to a local `audit_logs` table and shown in the Security Center.

**Not implemented in the prototype** — stated plainly so the UI is not mistaken for a guarantee:

- No authentication or role-based access control. The API is open to anything that can reach the port.
- No encryption at rest; files and the SQLite database are stored as-is.
- The audit log is an ordinary table — it is not tamper-evident.
- Docker Compose does **not** isolate the container network. Block egress with a host firewall for a real air gap.
- The frontend loads its fonts from Google Fonts at **build** time (then serves them itself), so building needs internet access once.

---

## 12 · Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests -q
```

36 tests cover the planner loop and its guardrails (step limit, loop detection, rogue tool calls, early finish), the tool allowlist, the review gate and approval flow, knowledge search, the airgap guard, and uploaded-document analysis (extraction, verification, unreadable files, duplicate filenames).

Frontend: `cd frontend && npx tsc --noEmit && npm run build`.

---

## 13 · Limitations

- **No language model runs by default.** The mock provider returns placeholder text; nothing reads the task with an LLM unless Ollama is enabled, and then only for the planner's choice.
- **Agentic runs use the fictional scenario.** The planner's tools wrap the demo agents, so an agentic run returns the demo findings whatever the task says. Agentic runs do not target an uploaded document and do not write report files.
- **Document analysis is keyword extraction.** It finds sentences containing risk terms (crack, leak, corrosion, overdue…) and quotes them. It does not understand the document, it misses anything phrased without those terms, and its "confidence" is match strength, not a probability.
- **No OCR and no vision model.** Images and scanned PDFs yield no text; the P&ID analysis is fixed demo data.
- **The Workbench "Run KAVACH" animation and several dashboard figures are baked demo data**, including the 94% / 8-of-9 verification numbers and the GPU readings.
- The knowledge base is a handful of chunks with hash embeddings, so similarity scores are low in absolute terms.
- Review reasons are returned by the API but not stored in their own database column.
- The Ollama adapter is covered only by its airgap-guard test; it has not been exercised against a running server.

## 14 · Roadmap

- Serve real open-weight models locally (Qwen3 for reasoning, a vision-language model, a code model) through vLLM or Ollama.
- Replace keyword extraction with LLM reasoning over retrieved evidence, keeping the excerpt re-check as the verifier.
- Let the agentic planner work on uploaded documents and produce deliverables.
- Real OCR and P&ID symbol/tag detection.
- Persistent vector store with dense + keyword retrieval.
- Authentication, RBAC, encryption at rest and a hash-chained audit log.
- Network-isolated deployment packaging.

---

<div align="center">
<sub>KAVACH AI · built for SIH 2026 · PS 26117 · MRPL</sub>
</div>
