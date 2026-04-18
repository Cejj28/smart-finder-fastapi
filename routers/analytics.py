"""
Analytics router — all endpoints are read-only and require a valid Django token.

Queries Django's shared PostgreSQL tables:
  - api_item     : reported items
  - auth_user    : registered users
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from datetime import datetime, timedelta, timezone
from typing import List

from database import get_db
from models import ApiItem, AuthUser
from schemas import (
    OverviewStats, TypeCount, StatusCount,
    LocationCount, DailyTrend, RecentItem
)
from auth import get_current_user

router = APIRouter()


# ── Overview ──────────────────────────────────────────────────────────────────

@router.get("/overview", response_model=OverviewStats)
async def stats_overview(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """
    High-level snapshot: total items, lost vs found split,
    user count, and status breakdown.
    """
    total_items = (await db.execute(select(func.count(ApiItem.id)))).scalar_one()
    total_lost = (await db.execute(
        select(func.count(ApiItem.id)).where(ApiItem.type == "Lost")
    )).scalar_one()
    total_found = (await db.execute(
        select(func.count(ApiItem.id)).where(ApiItem.type == "Found")
    )).scalar_one()
    total_users = (await db.execute(select(func.count(AuthUser.id)))).scalar_one()
    pending = (await db.execute(
        select(func.count(ApiItem.id)).where(ApiItem.status == "Pending Review")
    )).scalar_one()
    resolved = (await db.execute(
        select(func.count(ApiItem.id)).where(ApiItem.status == "Resolved")
    )).scalar_one()
    returned = (await db.execute(
        select(func.count(ApiItem.id)).where(ApiItem.status == "Returned to Owner")
    )).scalar_one()

    return OverviewStats(
        total_items=total_items,
        total_lost=total_lost,
        total_found=total_found,
        total_users=total_users,
        pending_review=pending,
        resolved=resolved,
        returned=returned,
    )


# ── By Type ───────────────────────────────────────────────────────────────────

@router.get("/by-type", response_model=List[TypeCount])
async def stats_by_type(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """Count of items grouped by type: Lost or Found."""
    result = await db.execute(
        select(ApiItem.type, func.count(ApiItem.id).label("count"))
        .group_by(ApiItem.type)
        .order_by(ApiItem.type)
    )
    return [TypeCount(type=row.type, count=row.count) for row in result.all()]


# ── By Status ─────────────────────────────────────────────────────────────────

@router.get("/by-status", response_model=List[StatusCount])
async def stats_by_status(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """Count of items grouped by status."""
    result = await db.execute(
        select(ApiItem.status, func.count(ApiItem.id).label("count"))
        .group_by(ApiItem.status)
        .order_by(func.count(ApiItem.id).desc())
    )
    return [StatusCount(status=row.status, count=row.count) for row in result.all()]


# ── By Location ───────────────────────────────────────────────────────────────

@router.get("/by-location", response_model=List[LocationCount])
async def stats_by_location(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """Top 10 locations by number of reported items."""
    result = await db.execute(
        select(ApiItem.location, func.count(ApiItem.id).label("count"))
        .group_by(ApiItem.location)
        .order_by(func.count(ApiItem.id).desc())
        .limit(10)
    )
    return [LocationCount(location=row.location, count=row.count) for row in result.all()]


# ── Trends ────────────────────────────────────────────────────────────────────

@router.get("/trends", response_model=List[DailyTrend])
async def stats_trends(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """
    Number of items submitted per day for the last 30 days.
    Returns a list ordered by date ascending — ready for charting.
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    result = await db.execute(
        select(
            cast(ApiItem.created_at, Date).label("date"),
            func.count(ApiItem.id).label("count"),
        )
        .where(ApiItem.created_at >= thirty_days_ago)
        .group_by(cast(ApiItem.created_at, Date))
        .order_by(cast(ApiItem.created_at, Date))
    )
    return [DailyTrend(date=row.date, count=row.count) for row in result.all()]


# ── Recent ────────────────────────────────────────────────────────────────────

@router.get("/recent", response_model=List[RecentItem])
async def stats_recent(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """The 5 most recently reported items — lightweight activity feed."""
    result = await db.execute(
        select(ApiItem)
        .order_by(ApiItem.created_at.desc())
        .limit(5)
    )
    return result.scalars().all()
