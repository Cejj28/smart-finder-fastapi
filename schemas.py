"""
Pydantic v2 schemas for FastAPI request/response validation.
All are response-only (analytics is read-only).
"""

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    service: str
    database: str


# ── Overview ──────────────────────────────────────────────────────────────────

class OverviewStats(BaseModel):
    total_items: int
    total_lost: int
    total_found: int
    total_users: int
    pending_review: int
    resolved: int
    returned: int


# ── By-Type ───────────────────────────────────────────────────────────────────

class TypeCount(BaseModel):
    type: str
    count: int


# ── By-Status ─────────────────────────────────────────────────────────────────

class StatusCount(BaseModel):
    status: str
    count: int


# ── By-Location ───────────────────────────────────────────────────────────────

class LocationCount(BaseModel):
    location: str
    count: int


# ── Trends ────────────────────────────────────────────────────────────────────

class DailyTrend(BaseModel):
    date: date
    count: int


# ── Recent items ──────────────────────────────────────────────────────────────

class RecentItem(BaseModel):
    id: int
    type: str
    item_name: str
    location: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ── ML Predictions ────────────────────────────────────────────────────────────

class InputData(BaseModel):
    text: str # [cite: 73]

class OutputData(BaseModel):
    label: str # [cite: 75]
    score: float # [cite: 76]