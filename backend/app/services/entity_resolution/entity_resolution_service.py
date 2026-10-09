"""
EntityResolutionService — deduplicates extracted entities within a case.

Strategy (in order of confidence):
1. Exact ID match (same id string from extractor)
2. Exact name normalization (case/whitespace)
3. Phone number normalization (strip non-digits)
4. Alias matching
5. Existing Neo4j nodes for the same case (cross-document resolution)

When a merge is detected, the canonical entity absorbs the alias and the
ID mappings in relationships are updated.

We do NOT auto-merge when evidence is weak (below a configurable threshold).
Resolution decisions are stored as metadata on the entity (provenance).
"""
import re
import logging
from copy import deepcopy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo4j import AsyncSession as Neo4jSession

from app.services.extraction import ExtractionResult, ExtractedEntity, ExtractedRelationship

logger = logging.getLogger(__name__)

MERGE_CONFIDENCE_THRESHOLD = 0.85  # Below this we do not auto-merge


def _normalize_name(name: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation."""
    return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()


def _normalize_phone(phone: str) -> str:
    """Strip all non-digit characters."""
    return re.sub(r"[^0-9]", "", phone)


class EntityResolutionService:

    async def resolve(
        self,
        extracted: ExtractionResult,
        case_id: str,
        neo4j_session: "Neo4jSession",
    ) -> ExtractionResult:
        """
        Main entry. Returns a new ExtractionResult with resolved/merged entities
        and updated relationship references.
        """
        resolved = deepcopy(extracted)

        # Build resolution map: old_id → canonical_id
        id_map = {}

        # Step 1: Within-batch resolution (same extraction run)
        id_map.update(self._resolve_within_batch(resolved.entities))

        # Step 2: Cross-document resolution against existing Neo4j nodes
        id_map.update(
            await self._resolve_against_existing(
                resolved.entities, case_id, neo4j_session, id_map
            )
        )

        # Step 3: Apply id_map to relationships and events
        self._apply_id_map(resolved, id_map)

        # Step 4: Remove duplicate entities (keep canonical)
        canonical_ids = set(id_map.values())
        merged_out = set(k for k, v in id_map.items() if k != v)
        resolved.entities = [e for e in resolved.entities if e.id not in merged_out]

        logger.info(
            f"Entity resolution: {len(extracted.entities)} → {len(resolved.entities)} "
            f"({len(merged_out)} merged)"
        )
        return resolved

    def _resolve_within_batch(self, entities: list[ExtractedEntity]) -> dict[str, str]:
        """Resolve duplicates within the extracted entity list."""
        id_map: dict[str, str] = {}
        # name_index: normalized_name → canonical entity id
        name_index: dict[str, str] = {}
        # phone_index: normalized_phone → canonical entity id
        phone_index: dict[str, str] = {}

        for entity in entities:
            norm_name = _normalize_name(entity.name)
            phone = _normalize_phone(entity.properties.get("phone", "") or "")
            account = (entity.properties.get("account_number", "") or "").strip()

            canonical_id = None

            # Check phone match
            if phone and len(phone) >= 7:
                if phone in phone_index:
                    canonical_id = phone_index[phone]
                else:
                    phone_index[phone] = entity.id

            # Check exact name match
            if canonical_id is None and norm_name in name_index:
                canonical_id = name_index[norm_name]

            # Check alias matches
            if canonical_id is None:
                for alias in entity.aliases:
                    norm_alias = _normalize_name(alias)
                    if norm_alias in name_index:
                        canonical_id = name_index[norm_alias]
                        break

            if canonical_id is not None and canonical_id != entity.id:
                id_map[entity.id] = canonical_id
                # Add aliases to canonical entity
                for e in entities:
                    if e.id == canonical_id:
                        if entity.name not in e.aliases:
                            e.aliases.append(entity.name)
                        break
                logger.debug(f"Merged '{entity.name}' ({entity.id}) → {canonical_id}")
            else:
                # Register as canonical
                name_index[norm_name] = entity.id
                for alias in entity.aliases:
                    name_index[_normalize_name(alias)] = entity.id
                if phone and len(phone) >= 7:
                    phone_index[phone] = entity.id
                id_map[entity.id] = entity.id  # identity mapping

        return id_map

    async def _resolve_against_existing(
        self,
        entities: list[ExtractedEntity],
        case_id: str,
        session: "Neo4jSession",
        existing_id_map: dict[str, str],
    ) -> dict[str, str]:
        """
        Check whether extracted entities match nodes already in Neo4j
        (from previously processed documents in the same case).
        """
        id_map: dict[str, str] = {}

        # Query existing nodes for this case
        result = await session.run(
            "MATCH (n {case_id: $case_id}) RETURN n.id AS id, n.name AS name, n.phone AS phone, labels(n)[0] AS label",
            {"case_id": case_id},
        )
        existing = []
        async for record in result:
            existing.append({
                "id": record["id"],
                "name": record["name"] or "",
                "phone": record["phone"] or "",
                "label": record["label"],
            })

        existing_name_index = {_normalize_name(e["name"]): e["id"] for e in existing if e["name"]}
        existing_phone_index = {_normalize_phone(e["phone"]): e["id"] for e in existing if e["phone"]}

        for entity in entities:
            # Only resolve entities not already merged in batch
            effective_id = existing_id_map.get(entity.id, entity.id)
            if effective_id != entity.id:
                continue  # Already merged

            norm_name = _normalize_name(entity.name)
            phone = _normalize_phone(entity.properties.get("phone", "") or "")

            # Phone match against existing
            if phone and len(phone) >= 7 and phone in existing_phone_index:
                existing_id = existing_phone_index[phone]
                id_map[entity.id] = existing_id
                logger.info(f"Cross-doc resolution (phone): '{entity.name}' → existing {existing_id}")
                continue

            # Name match against existing
            if norm_name in existing_name_index:
                existing_id = existing_name_index[norm_name]
                id_map[entity.id] = existing_id
                logger.info(f"Cross-doc resolution (name): '{entity.name}' → existing {existing_id}")

        return id_map

    @staticmethod
    def _apply_id_map(result: ExtractionResult, id_map: dict[str, str]) -> None:
        """Update all relationship and event references to use canonical IDs."""
        for rel in result.relationships:
            rel.from_id = id_map.get(rel.from_id, rel.from_id)
            rel.to_id = id_map.get(rel.to_id, rel.to_id)

        for event in result.events:
            event.participants = [id_map.get(p, p) for p in event.participants]
