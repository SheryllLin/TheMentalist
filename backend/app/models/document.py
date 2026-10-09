"""
Document model — tracks uploaded investigation files and their processing state.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, BigInteger, DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.postgres import Base


class DocumentType(str, enum.Enum):
    PDF = "PDF"
    TXT = "TXT"
    DOCX = "DOCX"
    CSV = "CSV"
    JSON = "JSON"
    UNKNOWN = "UNKNOWN"


class ProcessingStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType), nullable=False, default=DocumentType.UNKNOWN
    )
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    # Extracted plain text content (stored for re-processing without re-parsing)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SAEnum(ProcessingStatus), nullable=False, default=ProcessingStatus.UPLOADED
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    case = relationship("Case", back_populates="documents")
    uploader = relationship("User", back_populates="documents_uploaded")

    def __repr__(self) -> str:
        return f"<Document {self.original_filename} [{self.processing_status}]>"
