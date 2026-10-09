from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from app.models.document import DocumentType, ProcessingStatus


class DocumentOut(BaseModel):
    id: UUID
    case_id: UUID
    filename: str
    original_filename: str
    document_type: DocumentType
    file_size_bytes: Optional[int]
    processing_status: ProcessingStatus
    processing_error: Optional[str]
    uploaded_by: UUID
    uploaded_at: datetime
    processed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    document: DocumentOut
    job_id: UUID
    message: str
