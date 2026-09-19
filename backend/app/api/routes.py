"""All KAVACH AI HTTP routes."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from .. import config
from ..agents import orchestrator
from ..database import db
from ..models.providers import all_providers
from ..models.router import routing_rules
from ..schemas.schemas import (DemoRunRequest, HealthResponse, ReviewRequest,
                               TaskCreate)
from ..security.guard import ValidationError, safe_join, validate_upload
from ..security.middleware import write_audit
from ..services import knowledge as knowledge_service
from ..services import system_status
from ..services.deliverables import optional_formats

router = APIRouter(prefix="/api")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Health / system ----------------------------------------------------------
@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", mode=config.KAVACH_MODE,
                          version=config.VERSION, app=config.APP_NAME)


@router.get("/system/status")
def system_status_endpoint():
    return system_status.snapshot()


# --- Documents ----------------------------------------------------------------
@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    data = await file.read()
    try:
        safe_name, ext = validate_upload(file.filename or "upload", len(data))
        target = safe_join(config.UPLOADS_DIR, safe_name)
    except ValidationError as exc:
        write_audit("document.upload", detail=str(exc), outcome="rejected")
        raise HTTPException(status_code=400, detail=str(exc))

    config.ensure_dirs()
    with open(target, "wb") as fh:
        fh.write(data)

    doc_id = db.insert("documents", {
        "name": safe_name,
        "filename": safe_name,
        "path": str(target),
        "doc_type": ext,
        "size_bytes": len(data),
        "pages": 0,
        "status": "uploaded",
        "summary": f"User-uploaded {ext} document.",
        "created_at": _now(),
    })
    write_audit("document.upload", detail=f"stored {safe_name} ({len(data)} bytes)")
    return db.fetch_one("SELECT * FROM documents WHERE id=?", (doc_id,))


@router.get("/documents")
def list_documents():
    return db.fetch_all("SELECT * FROM documents ORDER BY id")


@router.get("/documents/{doc_id}")
def get_document(doc_id: int):
    doc = db.fetch_one("SELECT * FROM documents WHERE id=?", (doc_id,))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


def _extract_document_text(path: str, doc_type: str) -> str:
    """Extract readable text without making document analysis cloud-dependent."""
    from pathlib import Path

    source = Path(path)
    if doc_type in {"txt", "csv", "py"}:
        return source.read_text(encoding="utf-8", errors="replace")
    if doc_type == "docx":
        from docx import Document

        document = Document(str(source))
        return "\n".join(p.text for p in document.paragraphs)
    if doc_type == "pdf":
        try:
            from pypdf import PdfReader

            return "\n".join(page.extract_text() or "" for page in PdfReader(str(source)).pages)
        except ImportError:
            return "PDF text extraction requires the optional pypdf package."
    return ""


@router.post("/documents/{doc_id}/analyze")
def analyze_document(doc_id: int, payload: TaskCreate):
    """Run the local agent pipeline for one uploaded document."""
    document = db.fetch_one("SELECT * FROM documents WHERE id=?", (doc_id,))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    text = _extract_document_text(document["path"], document["doc_type"])
    task_text = payload.title + " " + (payload.description or "")
    task_id = db.insert("tasks", {
        "title": payload.title,
        "description": f"Document {document['filename']}: {text[:4000]}",
        "task_type": payload.task_type or "document_analysis",
        "status": "running",
        "run_id": None,
        "created_at": _now(),
    })
    run = orchestrator.run_pipeline(
        task_text=task_text,
        scenario_name=f"document:{document['filename']}",
        task_id=task_id,
        document=document,
        document_text=text,
    )
    db.execute("UPDATE tasks SET status=?, run_id=? WHERE id=?",
               ("completed", run["run"]["id"], task_id))
    return {"task": db.fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,)), "run": run}


# --- Tasks --------------------------------------------------------------------
@router.post("/tasks")
def create_task(payload: TaskCreate):
    from ..models.router import classify

    task_type = payload.task_type or classify(payload.title + " " + (payload.description or ""))
    task_id = db.insert("tasks", {
        "title": payload.title,
        "description": payload.description or "",
        "task_type": task_type,
        "status": "running",
        "run_id": None,
        "created_at": _now(),
    })
    # Kick off the agent run synchronously (mock).
    run = orchestrator.run_pipeline(
        task_text=payload.title + " " + (payload.description or ""),
        scenario_name="refinery_inspection",
        task_id=task_id,
    )
    run_id = run["run"]["id"]
    db.execute("UPDATE tasks SET status=?, run_id=? WHERE id=?",
               ("completed", run_id, task_id))
    write_audit("task.create", detail=f"task {task_id} -> run {run_id}")
    task = db.fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))
    return {"task": task, "run_id": run_id, "run": run}


@router.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = db.fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    run = orchestrator.get_run(task["run_id"]) if task["run_id"] else None
    return {"task": task, "run": run}


# --- Demo ---------------------------------------------------------------------
@router.post("/demo/run")
def demo_run(payload: DemoRunRequest | None = None):
    scenario_name = (payload.scenario if payload else None) or "refinery_inspection"
    write_audit("demo.run", detail=f"scenario={scenario_name}")
    run = orchestrator.run_pipeline(
        task_text="Inspect Unit 4 P&ID and inspection report for corrosion and integrity issues",
        scenario_name=scenario_name,
    )
    return run


@router.get("/demo/stream")
async def demo_stream():
    """Server-sent events emitting each pipeline step as it 'runs'."""
    async def event_gen():
        run = orchestrator.run_pipeline(
            task_text="Inspect Unit 4 P&ID and inspection report (streaming demo)",
            scenario_name="refinery_inspection",
        )
        for step in run["steps"]:
            payload = {"agent": step["agent"], "message": step["message"],
                       "status": step["status"], "detail": step["detail"]}
            yield f"event: step\ndata: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.15)
        summary = {"run_id": run["run"]["id"],
                   "verification_score": run["run"]["verification_score"],
                   "evidence_backed": run["run"]["evidence_backed"],
                   "findings": len(run["findings"]),
                   "deliverables": len(run["deliverables"])}
        yield f"event: complete\ndata: {json.dumps(summary)}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


# --- Agent runs ---------------------------------------------------------------
@router.get("/agents/runs")
def list_runs():
    return orchestrator.list_runs()


@router.get("/agents/runs/{run_id}")
def get_run(run_id: int):
    run = orchestrator.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


# --- Models -------------------------------------------------------------------
@router.get("/models")
def list_models():
    models = db.fetch_all("SELECT * FROM models ORDER BY id")
    providers = {name: p.health() for name, p in all_providers().items()}
    return {
        "models": models,
        "routing_rules": routing_rules(),
        "providers": providers,
        "active_provider": "mock-local",
    }


# --- Knowledge ----------------------------------------------------------------
@router.get("/knowledge")
def knowledge():
    return knowledge_service.stats()


# --- Audit logs ---------------------------------------------------------------
@router.get("/audit-logs")
def audit_logs(limit: int = 100):
    limit = max(1, min(limit, 1000))
    return db.fetch_all("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))


# --- Review -------------------------------------------------------------------
def _review(finding_id: int, decision: str, payload: ReviewRequest | None):
    finding = db.fetch_one("SELECT * FROM findings WHERE id=?", (finding_id,))
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    reviewer = (payload.reviewer if payload else None) or "inspector@kavach.local"
    note = (payload.note if payload else "") or ""
    db.insert("reviews", {
        "finding_id": finding_id,
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "created_at": _now(),
    })
    db.execute("UPDATE findings SET review_status=? WHERE id=?", (decision, finding_id))
    write_audit(f"review.{decision}", actor=reviewer,
                detail=f"finding {finding_id}: {note}")
    return db.fetch_one("SELECT * FROM findings WHERE id=?", (finding_id,))


@router.post("/review/{finding_id}/approve")
def approve_finding(finding_id: int, payload: ReviewRequest | None = None):
    return {"ok": True, "finding": _review(finding_id, "approved", payload)}


@router.post("/review/{finding_id}/reject")
def reject_finding(finding_id: int, payload: ReviewRequest | None = None):
    return {"ok": True, "finding": _review(finding_id, "rejected", payload)}


# --- Deliverables -------------------------------------------------------------
@router.get("/deliverables")
def list_deliverables():
    return {
        "deliverables": db.fetch_all("SELECT * FROM deliverables ORDER BY id DESC"),
        "optional_formats": optional_formats(),
    }


@router.get("/deliverables/{deliverable_id}/download")
def download_deliverable(deliverable_id: int):
    d = db.fetch_one("SELECT * FROM deliverables WHERE id=?", (deliverable_id,))
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    import os

    if not os.path.exists(d["path"]):
        raise HTTPException(status_code=410, detail="Deliverable file missing on disk")
    write_audit("deliverable.download", detail=f"id={deliverable_id} {d['filename']}")
    return FileResponse(d["path"], filename=d["filename"])
