"""
InvestigationReasoner — handles AI assistant queries.

Design:
- Receives a natural-language question from an investigator.
- Determines the best Cypher query strategy (from a controlled set of patterns).
- Queries Neo4j.
- Passes results + question to LLM for a grounded natural-language answer.
- Returns answer + evidence citations.

IMPORTANT: LLM does NOT generate Cypher directly.
The system maps question intent to safe, validated query templates.
This prevents Cypher injection and limits blast radius.
"""
import logging
import re
from typing import Any

from app.ai.extraction import INVESTIGATION_SYSTEM_PROMPT
from app.ai.provider import LLMProvider
from neo4j import AsyncSession as Neo4jSession

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# Safe query template registry
# -----------------------------------------------------------------
QUERY_TEMPLATES = {
    "most_connected": {
        "description": "Find the most connected entities",
        "cypher": """
            MATCH (n {case_id: $case_id})-[r]-()
            WITH n, labels(n) AS lbs, count(r) AS degree
            ORDER BY degree DESC LIMIT 10
            RETURN n.id AS id, n.name AS name, lbs AS labels, degree
        """,
        "params": {},
    },
    "neighbors_of": {
        "description": "Find entities connected to a specific entity",
        "cypher": """
            MATCH (n {case_id: $case_id})-[r]-(neighbor {case_id: $case_id})
            WHERE toLower(n.name) CONTAINS toLower($entity_name)
            RETURN n.name AS entity, type(r) AS rel_type,
                   neighbor.name AS neighbor,
                   labels(neighbor) AS neighbor_labels,
                   properties(r) AS rel_props
            LIMIT 50
        """,
        "params": ["entity_name"],
    },
    "transactions_involving": {
        "description": "Find transactions involving a specific entity",
        "cypher": """
            MATCH (n {case_id: $case_id})-[r]-(t:Transaction {case_id: $case_id})
            WHERE toLower(n.name) CONTAINS toLower($entity_name)
            RETURN n.name AS entity, type(r) AS rel_type,
                   t.amount AS amount, t.currency AS currency,
                   t.timestamp AS timestamp, t.description AS description,
                   properties(r) AS rel_props
            LIMIT 50
        """,
        "params": ["entity_name"],
    },
    "events_in_range": {
        "description": "Find events within a date range",
        "cypher": """
            MATCH (e:Event {case_id: $case_id})
            WHERE e.timestamp >= $start_date AND e.timestamp <= $end_date
            RETURN e.id AS id, e.name AS name, e.event_type AS event_type,
                   e.timestamp AS timestamp, e.description AS description
            ORDER BY e.timestamp
            LIMIT 50
        """,
        "params": ["start_date", "end_date"],
    },
    "connections_between": {
        "description": "Find connections between two entities",
        "cypher": """
            MATCH (a {case_id: $case_id}), (b {case_id: $case_id}),
                  path = shortestPath((a)-[*..8]-(b))
            WHERE toLower(a.name) CONTAINS toLower($entity_a)
              AND toLower(b.name) CONTAINS toLower($entity_b)
            RETURN [node IN nodes(path) | {id: node.id, name: node.name, labels: labels(node)}] AS path_nodes,
                   [rel IN relationships(path) | {type: type(rel), props: properties(rel)}] AS path_rels
            LIMIT 3
        """,
        "params": ["entity_a", "entity_b"],
    },
    "all_persons": {
        "description": "List all persons in the case",
        "cypher": """
            MATCH (p:Person {case_id: $case_id})
            RETURN p.id AS id, p.name AS name, p.phone AS phone, p.aliases AS aliases
            ORDER BY p.name
        """,
        "params": [],
    },
    "summary_all": {
        "description": "Get a full summary of all entities",
        "cypher": """
            MATCH (n {case_id: $case_id})
            WITH labels(n)[0] AS label, count(n) AS cnt
            RETURN label, cnt ORDER BY cnt DESC
        """,
        "params": [],
    },
}


class InvestigationReasoner:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def answer(
        self,
        question: str,
        case_id: str,
        neo4j_session: Neo4jSession,
    ) -> dict:
        """
        Main entry point for the investigation assistant.
        Returns: {answer, query_used, evidence, raw_results}
        """
        # Step 1: Determine query intent
        query_key, extra_params = self._classify_question(question)
        template = QUERY_TEMPLATES.get(query_key, QUERY_TEMPLATES["summary_all"])

        # Step 2: Execute safe query
        params = {"case_id": case_id, **extra_params}
        try:
            result = await neo4j_session.run(template["cypher"], params)
            rows = []
            async for record in result:
                rows.append(dict(record))
        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            rows = []

        # Step 3: Build context for LLM
        if not rows:
            evidence_text = "No relevant data found in the knowledge graph for this case."
        else:
            evidence_text = self._format_rows_for_context(rows)

        user_message = f"""
Investigation question: {question}

Case knowledge graph data:
{evidence_text}

Answer the investigator's question based ONLY on the above evidence.
Cite specific entities, relationships, and confidence scores where available.
"""

        # Step 4: Generate grounded answer
        answer_text = await self.llm.complete(
            system_prompt=INVESTIGATION_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.2,
            max_tokens=1500,
        )

        return {
            "answer": answer_text,
            "query_strategy": template["description"],
            "evidence": rows[:20],  # Return up to 20 evidence rows to frontend
            "total_evidence_rows": len(rows),
        }

    def _classify_question(self, question: str) -> tuple[str, dict]:
        """
        Map natural-language question to a query template + parameters.
        Uses simple keyword matching — deterministic, not LLM-generated.
        """
        q = question.lower()

        # "most connected" / "central" / "hub"
        if any(kw in q for kw in ["most connected", "most links", "central", "highest degree", "hub"]):
            return "most_connected", {}

        # "transactions involving X"
        tx_match = re.search(r"transactions?.*(?:involving|for|by|from|to)\s+(.+?)(?:\?|$)", q)
        if tx_match:
            return "transactions_involving", {"entity_name": tx_match.group(1).strip()}
        if "transaction" in q or "transfer" in q or "payment" in q:
            # Try to find a name
            name = self._extract_name_from_question(q)
            if name:
                return "transactions_involving", {"entity_name": name}

        # "connections between X and Y"
        between_match = re.search(
            r"(?:connect|relation|link|path).*between\s+(.+?)\s+and\s+(.+?)(?:\?|$)", q
        )
        if between_match:
            return "connections_between", {
                "entity_a": between_match.group(1).strip(),
                "entity_b": between_match.group(2).strip(),
            }

        # "connected to X" / "about X" / "involving X"
        about_match = re.search(
            r"(?:connected to|about|involving|related to|show.*)\s+([A-Z][a-z]+ [A-Z][a-z]+)", question
        )
        if about_match:
            return "neighbors_of", {"entity_name": about_match.group(1).strip()}

        # "everyone connected to X"
        name = self._extract_name_from_question(q)
        if name:
            return "neighbors_of", {"entity_name": name}

        # "all persons" / "list people"
        if any(kw in q for kw in ["all person", "list person", "all people", "who are"]):
            return "all_persons", {}

        return "summary_all", {}

    @staticmethod
    def _extract_name_from_question(text: str) -> str | None:
        """Look for a capitalized Name in the question."""
        match = re.search(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", text)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _format_rows_for_context(rows: list[dict]) -> str:
        lines = []
        for i, row in enumerate(rows[:30], 1):
            parts = []
            for k, v in row.items():
                if v is not None and v != "" and v != [] and k != "rel_props":
                    parts.append(f"{k}: {v}")
            # Include rel_props details
            if "rel_props" in row and row["rel_props"]:
                props = row["rel_props"]
                if "confidence" in props:
                    parts.append(f"confidence: {props['confidence']}")
                if "evidence_text" in props:
                    parts.append(f"evidence: {props['evidence_text'][:100]}")
            lines.append(f"{i}. " + " | ".join(parts))
        return "\n".join(lines)
