from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from app.models.case import CaseStatus, CasePriority


class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: CasePriority = CasePriority.MEDIUM


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None


class CaseOut(BaseModel):
    id: UUID
    case_number: str
    title: str
    description: Optional[str]
    status: CaseStatus
    priority: CasePriority
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseListOut(BaseModel):
    cases: list[CaseOut]
    total: int
