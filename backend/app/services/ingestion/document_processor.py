"""
DocumentProcessor — orchestrates the full ingestion pipeline for a single document.

Pipeline:
  1. Parse file → raw text / structured rows
  2. Extract entities + relationships (LLM for text; deterministic for CDR/Transactions)
  3. Entity resolution (deduplication within the case)
  4. Write graph to Neo4j (with retry on deadlock)
  5. Update document and job status in PostgreSQL
"""
import asyncio
import logging
import random
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, ProcessingStatus
from app.models.processing_job import ProcessingJob, JobStatus
from app.services.extraction import ExtractionService
from app.services.entity_resolution import EntityResolutionService
from app.services.graph import GraphService
from app.db.neo4j import get_neo4j_session
from app.services.ingestion.file_parser import FileParser

logger = logging.getLogger(__name__)

# Jitter so concurrent jobs don't all hammer Neo4j at the same millisecond
_STARTUP_JITTER_MAX = 2.0
_MAX_NEO4J_RETRIES = 3


async def _write_with_retry(case_id: str, resolved, max_retries: int = _MAX_NEO4J_RETRIES):
    """Write extraction results to Neo4j, retrying on deadlock."""
    for attempt in range(1, max_retries + 1):
        try:
            async with get_neo4j_session() as neo4j:
                return await GraphService.write_extraction_result(
                    session=neo4j,
                    case_id=case_id,
                    extracted=resolved,
                )
        except Exception as e:
            err_str = str(e)
            if "DeadlockDetected" in err_str and attempt < max_retries:
                wait = 1.5 * attempt + random.random()
                logger.warning(f"Neo4j deadlock on attempt {attempt}, retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            else:
                raise


class DocumentProcessor:

    @staticmethod
    async def process_document(
        db: AsyncSession,
        document: Document,
        job: ProcessingJob,
    ) -> None:
        """
        Main entry point. Runs the full pipeline.
        Updates job progress and document status throughout.
        """
        # Small random jitter so concurrent uploads don't all hit Neo4j together
        await asyncio.sleep(random.uniform(0, _STARTUP_JITTER_MAX))

        try:
            # --- Mark running ---
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            job.progress_pct = 5
            await db.commit()

            # --- Step 1: Parse ---
            logger.info(f"Parsing document: {document.original_filename}")
            parsed = FileParser.parse(document.storage_path, document.original_filename)
            document.extracted_text = parsed.raw_text
            job.progress_pct = 20
            await db.commit()

            # --- Step 2: Extract entities & relationships ---
            logger.info(f"Extracting from: {document.original_filename}")
            extraction_service = ExtractionService()

            if parsed.schema_type in ("CDR", "TRANSACTIONS") and parsed.structured_rows:
                extracted = extraction_service.extract_structured(
                    rows=parsed.structured_rows,
                    schema_type=parsed.schema_type,
                    document_id=str(document.id),
                    case_id=str(document.case_id),
                )
            else:
                extracted = await extraction_service.extract_from_text(
                    text=parsed.raw_text,
                    document_id=str(document.id),
                    case_id=str(document.case_id),
                )

            job.progress_pct = 60
            await db.commit()

            # --- Step 3: Entity resolution ---
            logger.info("Running entity resolution")
            resolver = EntityResolutionService()
            async with get_neo4j_session() as neo4j:
                resolved = await resolver.resolve(
                    extracted=extracted,
                    case_id=str(document.case_id),
                    neo4j_session=neo4j,
                )

            job.progress_pct = 75
            await db.commit()

            # --- Step 4: Write to Neo4j (with deadlock retry) ---
            logger.info("Writing graph to Neo4j")
            stats = await _write_with_retry(str(document.case_id), resolved)

            job.progress_pct = 95
            await db.commit()

            # --- Done ---
            document.processing_status = ProcessingStatus.PROCESSED
            document.processed_at = datetime.now(timezone.utc)
            job.status = JobStatus.COMPLETED
            job.progress_pct = 100
            job.completed_at = datetime.now(timezone.utc)
            job.result_summary = stats
            await db.commit()

            logger.info(f"Document {document.id} processed: {stats}")

        except Exception as e:
            logger.error(f"Document processing failed: {e}", exc_info=True)
            document.processing_status = ProcessingStatus.FAILED
            document.processing_error = str(e)[:500]
            job.status = JobStatus.FAILED
            job.error_message = str(e)[:500]
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            raise
