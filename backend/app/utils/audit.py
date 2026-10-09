"""
Audit logging helper.
Call log_action() anywhere in route handlers to record investigator activity.
"""
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def log_action(
    db: AsyncSession,
    action: str,
    user_id: Optional[UUID] = None,
    case_id: Optional[UUID] = None,
    metadata: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        case_id=case_id,
        action=action,
        action_metadata=metadata or {},
        ip_address=ip_address,
    )
    db.add(entry)
