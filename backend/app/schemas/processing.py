from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from app.models.processing_job import JobStatus


class ProcessingJobOut(BaseModel):
    id: UUID
    case_id: UUID
    document_id: Optional[UUID]
    job_type: str
    status: JobStatus
    progress_pct: int
    result_summary: Optional[dict]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
