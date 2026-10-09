from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    case_id: Optional[UUID]
    action: str
    action_metadata: Optional[dict]
    ip_address: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}
