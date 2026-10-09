"""
Helper to verify a user has access to a specific case.
ADMINs can access all cases; everyone else must be a CaseMember.
"""
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseMember
from app.models.user import User, UserRole


async def get_case_or_403(
    db: AsyncSession,
    case_id: UUID,
    current_user: User,
) -> Case:
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # ADMINs can see everything
    if current_user.role == UserRole.ADMIN:
        return case

    # Creator always has access
    if case.created_by == current_user.id:
        return case

    # Check membership
    member_result = await db.execute(
        select(CaseMember).where(
            CaseMember.case_id == case_id,
            CaseMember.user_id == current_user.id,
        )
    )
    if member_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this case",
        )
    return case
