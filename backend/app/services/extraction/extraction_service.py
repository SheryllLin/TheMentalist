"""
ExtractionService — runs entity and relationship extraction on document content.

Two paths:
1. Unstructured text → LLM extraction
2. Known structured schemas (CDR, TRANSACTIONS) → deterministic parser

Both produce the same ExtractionResult format.
"""
import hashlib
import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.ai.extraction import EXTRACTION_SYSTEM_PROMPT
from app.ai.provider import get_llm_provider

logger = logging.getLogger(__name__)

# Max characters sent to LLM in a single chunk
LLM_CHUNK_SIZE = 8000


@dataclass
class ExtractedEntity:
    id: str
    type: str
    name: str
    properties: dict = field(default_factory=dict)
    aliases: list[str] = field(default_factory=list)
    evidence_text: str = ""
    document_id: str = ""
    case_id: str = ""


@dataclass
class ExtractedRelationship:
    from_id: str
    from_type: str
    to_id: str
    to_type: str
    type: str
    properties: dict = field(default_factory=dict)
    evidence_text: str = ""
    document_id: str = ""
    case_id: str = ""
    confidence: float = 0.8


@dataclass
class ExtractedEvent:
    id: str
    name: str
    event_type: str
    timestamp: str
    description: str
    location: str = ""
    participants: list[str] = field(default_factory=list)
    document_id: str = ""
    case_id: str = ""


@dataclass
class ExtractionResult:
    entities: list[ExtractedEntity] = field(default_factory=list)
    relationships: list[ExtractedRelationship] = field(default_factory=list)
    events: list[ExtractedEvent] = field(default_factory=list)

    def merge(self, other: "ExtractionResult") -> None:
        """Merge another result into this one (for multi-chunk processing)."""
        existing_ids = {e.id for e in self.entities}
        for entity in other.entities:
            if entity.id not in existing_ids:
                self.entities.append(entity)
                existing_ids.add(entity.id)
        self.relationships.extend(other.relationships)
        self.events.extend(other.events)


def _stable_id(label: str, name: str) -> str:
    """Generate a stable, deterministic ID from label + name."""
    slug = re.sub(r"[^a-z0-9]+", "-", f"{label}-{name}".lower()).strip("-")
    return slug[:80]


class ExtractionService:

    def __init__(self):
        self.llm = get_llm_provider()

    # ------------------------------------------------------------------
    # LLM-based extraction for unstructured text
    # ------------------------------------------------------------------

    async def extract_from_text(
        self,
        text: str,
        document_id: str,
        case_id: str,
    ) -> ExtractionResult:
        result = ExtractionResult()

        # Split into chunks if text is long
        chunks = self._chunk_text(text, LLM_CHUNK_SIZE)
        logger.info(f"Extracting from {len(chunks)} text chunks (document {document_id})")

        for i, chunk in enumerate(chunks):
            logger.debug(f"Processing chunk {i+1}/{len(chunks)}")
            try:
                chunk_result = await self._extract_chunk(chunk, document_id, case_id)
                result.merge(chunk_result)
            except Exception as e:
                logger.warning(f"Chunk {i+1} extraction failed: {e}")

        return result

    async def _extract_chunk(
        self, text: str, document_id: str, case_id: str
    ) -> ExtractionResult:
        try:
            raw = await self.llm.complete_json(
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                user_message=f"Extract entities, relationships, and events from this investigation document:\n\n{text}",
            )
            return self._parse_llm_response(raw, document_id, case_id)
        except (ValueError, KeyError, TypeError) as e:
            # LLM returned non-JSON or malformed response — return empty result
            # rather than crashing the whole pipeline.
            logger.warning(f"LLM extraction parse error (doc {document_id}): {e}. Returning empty extraction.")
            return ExtractionResult()

    def _parse_llm_response(
        self, raw: dict, document_id: str, case_id: str
    ) -> ExtractionResult:
        result = ExtractionResult()

        for e in raw.get("entities", []):
            entity = ExtractedEntity(
                id=e.get("id", _stable_id(e.get("type", "entity"), e.get("name", "unknown"))),
                type=e.get("type", "Entity"),
                name=e.get("name", "Unknown"),
                properties=e.get("properties", {}),
                aliases=e.get("aliases", []),
                evidence_text=e.get("evidence_text", ""),
                document_id=document_id,
                case_id=case_id,
            )
            result.entities.append(entity)

        for r in raw.get("relationships", []):
            conf = r.get("properties", {}).get("confidence", 0.8)
            rel = ExtractedRelationship(
                from_id=r.get("from_id", ""),
                from_type=r.get("from_type", "Entity"),
                to_id=r.get("to_id", ""),
                to_type=r.get("to_type", "Entity"),
                type=r.get("type", "CONNECTED_TO"),
                properties=r.get("properties", {}),
                evidence_text=r.get("evidence_text", ""),
                document_id=document_id,
                case_id=case_id,
                confidence=float(conf),
            )
            result.relationships.append(rel)

        for ev in raw.get("events", []):
            event = ExtractedEvent(
                id=ev.get("id", f"event-{document_id[:8]}-{uuid.uuid4().hex[:8]}"),
                name=ev.get("name", "Unknown Event"),
                event_type=ev.get("event_type", "OTHER"),
                timestamp=ev.get("timestamp", ""),
                description=ev.get("description", ""),
                location=ev.get("location", ""),
                participants=ev.get("participants", []),
                document_id=document_id,
                case_id=case_id,
            )
            result.events.append(event)

        return result

    # ------------------------------------------------------------------
    # Deterministic extraction for known structured schemas
    # ------------------------------------------------------------------

    def extract_structured(
        self,
        rows: list[dict],
        schema_type: str,
        document_id: str,
        case_id: str,
    ) -> ExtractionResult:
        if schema_type == "CDR":
            return self._extract_cdr(rows, document_id, case_id)
        elif schema_type == "TRANSACTIONS":
            return self._extract_transactions(rows, document_id, case_id)
        else:
            # Generic: convert to text and try LLM (but return empty for now)
            return ExtractionResult()

    def _extract_cdr(
        self, rows: list[dict], document_id: str, case_id: str
    ) -> ExtractionResult:
        """
        CDR (Call Detail Record) deterministic extractor.
        Creates Phone entities and CALLED relationships.
        """
        result = ExtractionResult()
        phone_registry: dict[str, ExtractedEntity] = {}

        def get_phone(number: str) -> ExtractedEntity:
            key = re.sub(r"[^+\d]", "", str(number))
            if key not in phone_registry:
                entity = ExtractedEntity(
                    id=_stable_id("phone", key),
                    type="Phone",
                    name=key,
                    properties={"number": key},
                    document_id=document_id,
                    case_id=case_id,
                )
                phone_registry[key] = entity
                result.entities.append(entity)
            return phone_registry[key]

        for row in rows:
            caller_str = str(row.get("caller", ""))
            receiver_str = str(row.get("receiver", ""))
            timestamp = str(row.get("timestamp", ""))
            duration = row.get("duration_sec", "")
            tower = row.get("cell_tower", "")

            caller = get_phone(caller_str)
            receiver = get_phone(receiver_str)

            # CALLED relationship
            result.relationships.append(
                ExtractedRelationship(
                    from_id=caller.id,
                    from_type="Phone",
                    to_id=receiver.id,
                    to_type="Phone",
                    type="CALLED",
                    properties={
                        "timestamp": timestamp,
                        "duration_sec": str(duration),
                        "cell_tower": tower,
                        "confidence": 1.0,
                        "source_document_id": document_id,
                        "extracted_by": "deterministic_cdr_parser",
                    },
                    evidence_text=f"CDR: {caller_str} called {receiver_str} at {timestamp} ({duration}s)",
                    document_id=document_id,
                    case_id=case_id,
                    confidence=1.0,
                )
            )

            # Create an Event for each call
            event_id = f"call-{_stable_id('phone', caller_str)}-{timestamp}".replace(" ", "-")
            result.events.append(
                ExtractedEvent(
                    id=event_id,
                    name=f"Call: {caller_str} → {receiver_str}",
                    event_type="CALL",
                    timestamp=timestamp,
                    description=f"Duration: {duration}s | Tower: {tower}",
                    participants=[caller.id, receiver.id],
                    document_id=document_id,
                    case_id=case_id,
                )
            )

        return result

    def _extract_transactions(
        self, rows: list[dict], document_id: str, case_id: str
    ) -> ExtractionResult:
        """
        Financial transaction deterministic extractor.
        Creates BankAccount and Transaction entities, plus TRANSFERRED/RECEIVED_BY relationships.
        """
        result = ExtractionResult()
        account_registry: dict[str, ExtractedEntity] = {}

        def get_account(acc_number: str) -> ExtractedEntity:
            key = str(acc_number).strip()
            if key not in account_registry:
                entity = ExtractedEntity(
                    id=_stable_id("bankaccount", key),
                    type="BankAccount",
                    name=key,
                    properties={"account_number": key},
                    document_id=document_id,
                    case_id=case_id,
                )
                account_registry[key] = entity
                result.entities.append(entity)
            return account_registry[key]

        for row in rows:
            tx_id = str(row.get("tx_id", f"tx-{uuid.uuid4().hex[:8]}"))
            sender_acc = str(row.get("sender_account", "UNKNOWN"))
            receiver_acc = str(row.get("receiver_account", "UNKNOWN"))
            amount = row.get("amount", 0)
            currency = row.get("currency", "INR")
            timestamp = str(row.get("timestamp", ""))
            tx_type = str(row.get("transaction_type", "TRANSFER"))
            description = str(row.get("description", ""))

            sender = get_account(sender_acc)
            receiver = get_account(receiver_acc)

            # Transaction node
            tx_entity = ExtractedEntity(
                id=_stable_id("transaction", tx_id),
                type="Transaction",
                name=f"{currency} {amount} ({tx_id})",
                properties={
                    "amount": str(amount),
                    "currency": currency,
                    "timestamp": timestamp,
                    "transaction_type": tx_type,
                    "description": description,
                    "tx_id": tx_id,
                },
                evidence_text=f"Transaction {tx_id}: {sender_acc} → {receiver_acc} | {currency} {amount}",
                document_id=document_id,
                case_id=case_id,
            )
            result.entities.append(tx_entity)

            # TRANSFERRED: sender → transaction
            result.relationships.append(
                ExtractedRelationship(
                    from_id=sender.id,
                    from_type="BankAccount",
                    to_id=tx_entity.id,
                    to_type="Transaction",
                    type="TRANSFERRED",
                    properties={
                        "timestamp": timestamp,
                        "confidence": 1.0,
                        "source_document_id": document_id,
                        "extracted_by": "deterministic_transaction_parser",
                        "evidence_text": tx_entity.evidence_text,
                    },
                    evidence_text=tx_entity.evidence_text,
                    document_id=document_id,
                    case_id=case_id,
                    confidence=1.0,
                )
            )

            # RECEIVED_BY: transaction → receiver
            result.relationships.append(
                ExtractedRelationship(
                    from_id=tx_entity.id,
                    from_type="Transaction",
                    to_id=receiver.id,
                    to_type="BankAccount",
                    type="RECEIVED_BY",
                    properties={
                        "timestamp": timestamp,
                        "confidence": 1.0,
                        "source_document_id": document_id,
                        "extracted_by": "deterministic_transaction_parser",
                        "evidence_text": tx_entity.evidence_text,
                    },
                    evidence_text=tx_entity.evidence_text,
                    document_id=document_id,
                    case_id=case_id,
                    confidence=1.0,
                )
            )

            # Event
            result.events.append(
                ExtractedEvent(
                    id=_stable_id("event-tx", tx_id),
                    name=f"Transaction: {currency} {amount}",
                    event_type="TRANSACTION",
                    timestamp=timestamp,
                    description=f"{description} | {sender_acc} → {receiver_acc}",
                    participants=[sender.id, receiver.id, tx_entity.id],
                    document_id=document_id,
                    case_id=case_id,
                )
            )

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _chunk_text(text: str, chunk_size: int) -> list[str]:
        """Split text into chunks at paragraph boundaries."""
        if len(text) <= chunk_size:
            return [text]
        paragraphs = text.split("\n\n")
        chunks = []
        current = []
        current_len = 0
        for para in paragraphs:
            if current_len + len(para) > chunk_size and current:
                chunks.append("\n\n".join(current))
                current = [para]
                current_len = len(para)
            else:
                current.append(para)
                current_len += len(para)
        if current:
            chunks.append("\n\n".join(current))
        return chunks
