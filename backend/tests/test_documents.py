"""Tests for uploaded-document analysis: findings must come from the file itself."""
from __future__ import annotations

from app.services import document_analysis

REPORT = (
    "Compressor K-220 quarterly inspection.\n"
    "A hairline crack was observed on the discharge flange of K-220 and requires repair.\n"
    "Bearing vibration on K-220 is trending upward; recommend monitoring weekly.\n"
    "The lube oil cooler was cleaned and returned to service without remarks.\n"
)


def _upload(client, name: str, content: bytes) -> dict:
    res = client.post("/api/documents/upload", files={"file": (name, content)})
    assert res.status_code == 200, res.text
    return res.json()


def _analyze(client, doc_id: int) -> dict:
    res = client.post(f"/api/documents/{doc_id}/analyze", json={"title": "Review for defects"})
    assert res.status_code == 200, res.text
    return res.json()["run"]


def test_findings_are_extracted_from_the_uploaded_text(client):
    doc = _upload(client, "k220_report.txt", REPORT.encode())
    run = _analyze(client, doc["id"])

    titles = " ".join(f["title"] for f in run["findings"])
    assert "K-220" in titles and "P-101" not in titles  # nothing from the demo scenario
    assert run["findings"][0]["severity"] == "high"
    assert all(ev["source"] == doc["filename"] and ev["excerpt"] in REPORT.replace("\n", " ")
               for f in run["findings"] for ev in f["evidence"])
    assert run["run"]["verification_score"] == 100.0
    assert "vision_agent" in [s["agent"] for s in run["steps"] if s["status"] == "skipped"]
    # The high-severity finding is held for an engineer.
    assert run["run"]["status"] == "awaiting_review"
    assert run["findings"][0]["needs_review"] == 1


def test_document_without_risk_terms_yields_no_findings(client):
    doc = _upload(client, "notes.txt", b"The quarterly meeting was moved to Thursday afternoon.")
    run = _analyze(client, doc["id"])
    assert run["findings"] == []
    assert run["run"]["status"] == "completed"


def test_unreadable_upload_does_not_crash_the_run(client):
    doc = _upload(client, "broken.pdf", b"this is not a pdf")
    run = _analyze(client, doc["id"])
    assert run["findings"] == []
    assert any(s["status"] == "warning" for s in run["steps"])


def test_same_filename_uploads_do_not_overwrite(client):
    first = _upload(client, "dup.txt", b"first")
    second = _upload(client, "dup.txt", b"second")
    assert first["path"] != second["path"]
    assert open(first["path"], "rb").read() == b"first"


def test_seeded_demo_pdf_is_read_by_file_extension(client):
    # Seeded documents store a category ("report") in doc_type, not "pdf".
    doc = next(d for d in client.get("/api/documents").json()
               if d["filename"] == "inspection_report.pdf")
    run = _analyze(client, doc["id"])
    assert run["findings"], [s["detail"] for s in run["steps"]]
    assert all(ev["source"] == "inspection_report.pdf"
               for f in run["findings"] for ev in f["evidence"])


def test_analyze_unknown_document_is_404(client):
    assert client.post("/api/documents/999999/analyze", json={"title": "x"}).status_code == 404


def test_verification_catches_an_excerpt_that_is_not_in_the_document():
    findings = document_analysis.find_findings(REPORT, "r.txt")
    findings[0]["evidence"][0]["excerpt"] = "A sentence the document never contained."
    result = document_analysis.verify_findings(findings, REPORT)
    assert result["score"] < 100
    assert findings[0]["title"] in result["unsupported"]
