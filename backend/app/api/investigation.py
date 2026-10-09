"""
AI Investigation Assistant endpoint.
"""
import uuid
from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.neo4j import neo4j_session
from app.models.user import User
from app.services.auth import get_current_user
from app.ai.provider import get_llm_provider
from app.ai.reasoning import InvestigationReasoner
from app.utils.audit import log_action
from app.utils.case_access import get_case_or_403

router = APIRouter(tags=["investigation"])


class InvestigationQuery(BaseModel):
    question: str


@router.post("/cases/{case_id}/investigate")
async def investigate(
    case_id: uuid.UUID,
    payload: InvestigationQuery,
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)

    llm = get_llm_provider()
    reasoner = InvestigationReasoner(llm)
    result = await reasoner.answer(
        question=payload.question,
        case_id=str(case_id),
        neo4j_session=neo4j,
    )

    await log_action(
        db, "INVESTIGATION_QUERY",
        user_id=current_user.id,
        case_id=case_id,
        metadata={"question": payload.question[:200]},
    )

    return result
