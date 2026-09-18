"""Pydantic request/response schemas for the KAVACH AI API."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    mode: str
    version: str
    app: str


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = Field(default="", max_length=5000)
    task_type: Optional[str] = None


class DemoRunRequest(BaseModel):
    scenario: Optional[str] = "refinery_inspection"


class ReviewRequest(BaseModel):
    note: Optional[str] = Field(default="", max_length=2000)
    reviewer: Optional[str] = "inspector@kavach.local"


class GenericResponse(BaseModel):
    ok: bool = True
    detail: Optional[str] = None
    data: Optional[Any] = None
