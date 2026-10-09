"""
Document upload and management endpoints.
"""
import os
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.postgres import get_db
from app.models.document import Document, DocumentType, ProcessingStatus
from app.models.processing_job import ProcessingJob, JobStatus
from app.models.user import User
from app.schemas.document import DocumentOut, DocumentUploadResponse
from app.schemas.processing import ProcessingJobOut
from app.services.auth import get_current_user
from app.utils.audit import log_action
from app.utils.case_access import get_case_or_403

router = APIRouter(tags=["documents"])
settings = get_settings()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".csv", ".json"}
EXTENSION_TO_TYPE = {
    ".pdf": DocumentType.PDF,
    ".txt": DocumentType.TXT,
    ".docx": DocumentType.DOCX,
    ".csv": DocumentType.CSV,
    ".json": DocumentType.JSON,
}


def _get_upload_path(case_id: str) -> Path:
    path = Path(settings.upload_dir) / case_id
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.post("/cases/{case_id}/documents", response_model=DocumentUploadResponse,
             status_code=status.HTTP_201_CREATED)
async def upload_document(
    case_id: uuid.UUID,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify case access
    case = await get_case_or_403(db, case_id, current_user)

    # Validate file extension
    ext = Path(file.filename or "unknown").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' not supported. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # Validate file size
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    contents = await file.read()
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    # Save file
    upload_dir = _get_upload_path(str(case_id))
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    storage_path = upload_dir / stored_filename
    with open(storage_path, "wb") as f:
        f.write(contents)

    # Create document record
    doc = Document(
        case_id=case_id,
        filename=stored_filename,
        original_filename=file.filename or "unknown",
        document_type=EXTENSION_TO_TYPE.get(ext, DocumentType.UNKNOWN),
        storage_path=str(storage_path),
        file_size_bytes=len(contents),
        processing_status=ProcessingStatus.UPLOADED,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.flush()

    # Create processing job
    job = ProcessingJob(
        case_id=case_id,
        document_id=doc.id,
        job_type="document_processing",
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.flush()

    await log_action(
        db, "DOCUMENT_UPLOAD",
        user_id=current_user.id,
        case_id=case_id,
        metadata={"filename": file.filename, "document_id": str(doc.id)},
    )
    await db.commit()

    # Refresh for response
    await db.refresh(doc)
    await db.refresh(job)

    # Kick off background processing
    background_tasks.add_task(_process_document_background, str(doc.id), str(job.id))

    return DocumentUploadResponse(
        document=DocumentOut.model_validate(doc),
        job_id=job.id,
        message=f"Document uploaded. Processing started (job {job.id}).",
    )


async def _process_document_background(document_id: str, job_id: str) -> None:
    """
    Background task: runs the full ingestion pipeline.
    Uses a separate DB session (not the request session which is already closed).
    """
    from app.db.postgres import AsyncSessionLocal
    from app.services.ingestion.document_processor import DocumentProcessor
    from sqlalchemy import select as sa_select

    async with AsyncSessionLocal() as db:
        try:
            doc_result = await db.execute(
                sa_select(Document).where(Document.id == uuid.UUID(document_id))
            )
            doc = doc_result.scalar_one_or_none()

            job_result = await db.execute(
                sa_select(ProcessingJob).where(ProcessingJob.id == uuid.UUID(job_id))
            )
            job = job_result.scalar_one_or_none()

            if doc and job:
                await DocumentProcessor.process_document(db, doc, job)
        except Exception as e:
            logger.error(f"Background processing failed for document {document_id}: {e}", exc_info=True)


@router.get("/cases/{case_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    result = await db.execute(
        select(Document)
        .where(Document.case_id == case_id)
        .order_by(Document.uploaded_at.desc())
    )
    docs = result.scalars().all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/cases/{case_id}/documents/{document_id}", response_model=DocumentOut)
async def get_document(
    case_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    result = await db.execute(
        select(Document).where(
            Document.id == document_id, Document.case_id == case_id
        )
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentOut.model_validate(doc)


@router.get("/cases/{case_id}/jobs/{job_id}", response_model=ProcessingJobOut)
async def get_job_status(
    case_id: uuid.UUID,
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    result = await db.execute(
        select(ProcessingJob).where(
            ProcessingJob.id == job_id, ProcessingJob.case_id == case_id
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return ProcessingJobOut.model_validate(job)


@router.post("/cases/{case_id}/reprocess/{document_id}", response_model=ProcessingJobOut)
async def reprocess_document(
    case_id: uuid.UUID,
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-run the processing pipeline on an already-uploaded document."""
    await get_case_or_403(db, case_id, current_user)
    doc_result = await db.execute(
        select(Document).where(Document.id == document_id, Document.case_id == case_id)
    )
    doc = doc_result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.processing_status = ProcessingStatus.UPLOADED
    doc.processing_error = None

    job = ProcessingJob(
        case_id=case_id,
        document_id=doc.id,
        job_type="document_reprocessing",
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.flush()
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(_process_document_background, str(doc.id), str(job.id))
    return ProcessingJobOut.model_validate(job)
