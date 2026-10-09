"""
Case management endpoints.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.case import Case, CaseStatus, CasePriority, CaseMember
from app.models.user import User, UserRole
from app.schemas.case import CaseCreate, CaseUpdate, CaseOut, CaseListOut
from app.schemas.audit import AuditLogOut
from app.models.audit import AuditLog
from app.services.auth import get_current_user
from app.utils.audit import log_action
from app.utils.case_access import get_case_or_403

router = APIRouter(prefix="/cases", tags=["cases"])


def _generate_case_number() -> str:
    year = datetime.now(timezone.utc).year
    suffix = str(uuid.uuid4())[:8].upper()
    return f"CASE-{year}-{suffix}"


@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = Case(
        case_number=_generate_case_number(),
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=CaseStatus.ACTIVE,
        created_by=current_user.id,
    )
    db.add(case)
    await db.flush()

    # Creator is automatically a member
    membership = CaseMember(case_id=case.id, user_id=current_user.id)
    db.add(membership)

    await log_action(
        db, "CASE_CREATE",
        user_id=current_user.id,
        case_id=case.id,
        metadata={"case_number": case.case_number, "title": case.title},
    )
    return case


@router.get("", response_model=CaseListOut)
async def list_cases(
    status_filter: Optional[CaseStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        # Admins see all cases
        query = select(Case)
        count_query = select(func.count()).select_from(Case)
    else:
        # Others only see cases they're members of
        query = (
            select(Case)
            .join(CaseMember, CaseMember.case_id == Case.id)
            .where(CaseMember.user_id == current_user.id)
        )
        count_query = (
            select(func.count())
            .select_from(Case)
            .join(CaseMember, CaseMember.case_id == Case.id)
            .where(CaseMember.user_id == current_user.id)
        )

    if status_filter:
        query = query.where(Case.status == status_filter)
        count_query = count_query.where(Case.status == status_filter)

    query = query.order_by(Case.updated_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    total_result = await db.execute(count_query)
    cases = result.scalars().all()
    total = total_result.scalar_one()

    await log_action(db, "CASE_LIST", user_id=current_user.id)
    return CaseListOut(cases=[CaseOut.model_validate(c) for c in cases], total=total)


@router.get("/{case_id}", response_model=CaseOut)
async def get_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = await get_case_or_403(db, case_id, current_user)
    await log_action(db, "CASE_VIEW", user_id=current_user.id, case_id=case_id)
    return case


@router.put("/{case_id}", response_model=CaseOut)
async def update_case(
    case_id: uuid.UUID,
    payload: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = await get_case_or_403(db, case_id, current_user)

    if payload.title is not None:
        case.title = payload.title
    if payload.description is not None:
        case.description = payload.description
    if payload.status is not None:
        case.status = payload.status
    if payload.priority is not None:
        case.priority = payload.priority

    await log_action(
        db, "CASE_UPDATE",
        user_id=current_user.id,
        case_id=case_id,
        metadata=payload.model_dump(exclude_none=True),
    )
    return case


@router.get("/{case_id}/audit", response_model=list[AuditLogOut])
async def get_case_audit(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.case_id == case_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(200)
    )
    logs = result.scalars().all()
    return [AuditLogOut.model_validate(l) for l in logs]
