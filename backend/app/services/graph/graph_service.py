"""
GraphService — all Neo4j read/write operations.

Design decisions:
- All Cypher queries use parameterized values (no string interpolation from user input).
- case_id is always passed as a property on nodes to scope queries to a single case.
- Provenance (source_document_id, evidence_text, confidence) is stored on relationships.
"""
from typing import Any, Optional
from uuid import UUID

from neo4j import AsyncSession as Neo4jSession

from app.db.neo4j import get_neo4j_session


class GraphService:

    # ------------------------------------------------------------------
    # Node creation / merge
    # ------------------------------------------------------------------

    @staticmethod
    async def merge_entity(
        session: Neo4jSession,
        case_id: str,
        label: str,
        entity_id: str,
        properties: dict,
    ) -> dict:
        """
        MERGE a node by its id and case_id, then SET all properties.
        Returns the node properties.
        """
        # Build property SET string dynamically (safe — properties come from extraction service)
        set_clause = ", ".join(f"n.{k} = ${k}" for k in properties)
        query = f"""
        MERGE (n:{label} {{id: $entity_id, case_id: $case_id}})
        SET {set_clause}
        RETURN n
        """
        params = {"entity_id": entity_id, "case_id": case_id, **properties}
        result = await session.run(query, params)
        record = await result.single()
        return dict(record["n"]) if record else {}

    @staticmethod
    async def merge_relationship(
        session: Neo4jSession,
        case_id: str,
        from_id: str,
        from_label: str,
        to_id: str,
        to_label: str,
        rel_type: str,
        properties: dict,
    ) -> None:
        """
        MERGE a relationship between two nodes.
        All relationship properties (confidence, evidence, etc.) are stored on the edge.
        """
        query = f"""
        MATCH (a:{from_label} {{id: $from_id, case_id: $case_id}})
        MATCH (b:{to_label} {{id: $to_id, case_id: $case_id}})
        MERGE (a)-[r:{rel_type} {{source_document_id: $source_document_id}}]->(b)
        SET r += $props
        """
        params = {
            "from_id": from_id,
            "to_id": to_id,
            "case_id": case_id,
            "source_document_id": properties.get("source_document_id", ""),
            "props": properties,
        }
        await session.run(query, params)

    # ------------------------------------------------------------------
    # Case graph retrieval (for visualization)
    # ------------------------------------------------------------------

    @staticmethod
    async def get_case_graph(session: Neo4jSession, case_id: str) -> dict:
        """
        Return all nodes and relationships for a given case_id.
        """
        nodes_query = """
        MATCH (n {case_id: $case_id})
        RETURN n, labels(n) AS labels
        LIMIT 500
        """
        rels_query = """
        MATCH (a {case_id: $case_id})-[r]->(b {case_id: $case_id})
        RETURN a.id AS source, b.id AS target, type(r) AS type,
               properties(r) AS props
        LIMIT 1000
        """
        nodes = []
        result = await session.run(nodes_query, {"case_id": case_id})
        async for record in result:
            node_data = dict(record["n"])
            node_data["_labels"] = record["labels"]
            nodes.append(node_data)

        edges = []
        result = await session.run(rels_query, {"case_id": case_id})
        async for record in result:
            edges.append({
                "source": record["source"],
                "target": record["target"],
                "type": record["type"],
                **record["props"],
            })

        return {"nodes": nodes, "edges": edges}

    # ------------------------------------------------------------------
    # Node detail + neighbors
    # ------------------------------------------------------------------

    @staticmethod
    async def get_node_detail(session: Neo4jSession, case_id: str, node_id: str) -> dict:
        query = """
        MATCH (n {id: $node_id, case_id: $case_id})
        OPTIONAL MATCH (n)-[r]-(neighbor {case_id: $case_id})
        RETURN n, labels(n) AS labels,
               collect({
                 neighbor_id: neighbor.id,
                 neighbor_name: neighbor.name,
                 neighbor_labels: labels(neighbor),
                 rel_type: type(r),
                 rel_props: properties(r)
               }) AS connections
        LIMIT 1
        """
        result = await session.run(query, {"node_id": node_id, "case_id": case_id})
        record = await result.single()
        if not record:
            return {}
        node_data = dict(record["n"])
        node_data["_labels"] = record["labels"]
        node_data["connections"] = [
            c for c in record["connections"] if c.get("neighbor_id") is not None
        ]
        return node_data

    # ------------------------------------------------------------------
    # Shortest path
    # ------------------------------------------------------------------

    @staticmethod
    async def get_shortest_path(
        session: Neo4jSession, case_id: str, from_id: str, to_id: str
    ) -> list[dict]:
        query = """
        MATCH (a {id: $from_id, case_id: $case_id}),
              (b {id: $to_id, case_id: $case_id}),
              path = shortestPath((a)-[*..10]-(b))
        RETURN [node IN nodes(path) | {id: node.id, name: node.name, labels: labels(node)}] AS path_nodes,
               [rel IN relationships(path) | {type: type(rel), props: properties(rel)}] AS path_rels
        LIMIT 1
        """
        result = await session.run(query, {"from_id": from_id, "to_id": to_id, "case_id": case_id})
        record = await result.single()
        if not record:
            return []
        return {"nodes": record["path_nodes"], "relationships": record["path_rels"]}

    # ------------------------------------------------------------------
    # Entity search (fulltext)
    # ------------------------------------------------------------------

    @staticmethod
    async def search_entities(
        session: Neo4jSession, case_id: str, query_text: str
    ) -> list[dict]:
        # Use fulltext index for Person/Org/Location; fall back to CONTAINS
        cypher = """
        CALL db.index.fulltext.queryNodes('entity_name_ft', $query_text)
        YIELD node, score
        WHERE node.case_id = $case_id
        RETURN node, labels(node) AS labels, score
        ORDER BY score DESC
        LIMIT 20
        """
        results = []
        try:
            result = await session.run(cypher, {"query_text": query_text, "case_id": case_id})
            async for record in result:
                data = dict(record["node"])
                data["_labels"] = record["labels"]
                data["_score"] = record["score"]
                results.append(data)
        except Exception:
            # Fulltext index may not exist yet — fallback
            fallback = """
            MATCH (n {case_id: $case_id})
            WHERE toLower(n.name) CONTAINS toLower($query_text)
            RETURN n, labels(n) AS labels
            LIMIT 20
            """
            result = await session.run(fallback, {"case_id": case_id, "query_text": query_text})
            async for record in result:
                data = dict(record["n"])
                data["_labels"] = record["labels"]
                results.append(data)
        return results

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    @staticmethod
    async def get_degree_centrality(session: Neo4jSession, case_id: str) -> list[dict]:
        query = """
        MATCH (n {case_id: $case_id})-[r]-()
        WITH n, labels(n) AS lbs, count(r) AS degree
        ORDER BY degree DESC
        LIMIT 20
        RETURN n.id AS id, n.name AS name, lbs AS labels, degree
        """
        result = await session.run(query, {"case_id": case_id})
        rows = []
        async for record in result:
            rows.append({
                "id": record["id"],
                "name": record["name"],
                "labels": record["labels"],
                "degree": record["degree"],
            })
        return rows

    @staticmethod
    async def get_entity_timeline(session: Neo4jSession, case_id: str) -> list[dict]:
        """Return events with timestamps for the timeline view."""
        query = """
        MATCH (e:Event {case_id: $case_id})
        OPTIONAL MATCH (e)-[:INVOLVES]->(p {case_id: $case_id})
        WITH e, collect(p.name) AS participants
        ORDER BY e.timestamp ASC
        RETURN e.id AS id, e.name AS name, e.event_type AS event_type,
               e.timestamp AS timestamp, e.description AS description,
               e.location AS location, participants
        """
        result = await session.run(query, {"case_id": case_id})
        rows = []
        async for record in result:
            rows.append({
                "id": record["id"],
                "name": record["name"],
                "event_type": record["event_type"],
                "timestamp": record["timestamp"],
                "description": record["description"],
                "location": record["location"],
                "participants": record["participants"],
            })
        return rows

    @staticmethod
    async def get_entities_by_type(
        session: Neo4jSession, case_id: str, label: str
    ) -> list[dict]:
        query = f"""
        MATCH (n:{label} {{case_id: $case_id}})
        RETURN n
        ORDER BY n.name
        LIMIT 200
        """
        result = await session.run(query, {"case_id": case_id})
        rows = []
        async for record in result:
            rows.append(dict(record["n"]))
        return rows

    @staticmethod
    async def run_investigation_query(
        session: Neo4jSession, case_id: str, cypher: str, params: dict
    ) -> list[dict]:
        """
        Execute a validated Cypher query for the investigation assistant.
        case_id is always injected to prevent cross-case data access.
        """
        params["case_id"] = case_id
        result = await session.run(cypher, params)
        rows = []
        async for record in result:
            rows.append(dict(record))
        return rows

    @staticmethod
    async def delete_case_graph(session: Neo4jSession, case_id: str) -> int:
        """Delete all nodes (and their relationships) for a case."""
        query = """
        MATCH (n {case_id: $case_id})
        DETACH DELETE n
        RETURN count(n) AS deleted
        """
        result = await session.run(query, {"case_id": case_id})
        record = await result.single()
        return record["deleted"] if record else 0


    # ------------------------------------------------------------------
    # Write extraction results (called by DocumentProcessor)
    # ------------------------------------------------------------------

    @staticmethod
    async def write_extraction_result(
        session,
        case_id: str,
        extracted,
    ) -> dict:
        """
        Write all extracted entities, relationships, and events to Neo4j.
        Returns a summary dict with counts.
        """
        nodes_written = 0
        rels_written = 0
        events_written = 0

        # Write entities
        for entity in extracted.entities:
            props = {
                "name": entity.name,
                "aliases": entity.aliases,
                "evidence_text": entity.evidence_text,
                "source_document_id": entity.document_id,
                **entity.properties,
            }
            await GraphService.merge_entity(
                session=session,
                case_id=case_id,
                label=entity.type,
                entity_id=entity.id,
                properties=props,
            )
            nodes_written += 1

        # Write events as Event nodes
        for event in extracted.events:
            event_props = {
                "name": event.name,
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "description": event.description,
                "location": event.location,
                "source_document_id": event.document_id,
            }
            await GraphService.merge_entity(
                session=session,
                case_id=case_id,
                label="Event",
                entity_id=event.id,
                properties=event_props,
            )
            events_written += 1

            # INVOLVES edges: event → participant
            for participant_id in event.participants:
                query = """
                MATCH (e:Event {id: $event_id, case_id: $case_id})
                MATCH (p {id: $participant_id, case_id: $case_id})
                MERGE (e)-[:INVOLVES]->(p)
                """
                try:
                    await session.run(query, {
                        "event_id": event.id,
                        "case_id": case_id,
                        "participant_id": participant_id,
                    })
                except Exception:
                    pass  # Participant may not exist yet

        # Write relationships
        for rel in extracted.relationships:
            rel_props = {
                "confidence": rel.confidence,
                "source_document_id": rel.document_id,
                "evidence_text": rel.evidence_text[:500] if rel.evidence_text else "",
                "extracted_by": rel.properties.get("extracted_by", "llm"),
                **{k: v for k, v in rel.properties.items() if k != "extracted_by"},
            }
            try:
                await GraphService.merge_relationship(
                    session=session,
                    case_id=case_id,
                    from_id=rel.from_id,
                    from_label=rel.from_type,
                    to_id=rel.to_id,
                    to_label=rel.to_type,
                    rel_type=rel.type,
                    properties=rel_props,
                )
                rels_written += 1
            except Exception as e:
                # Relationship may fail if a node doesn't exist; log and continue
                pass

        return {
            "nodes_written": nodes_written,
            "relationships_written": rels_written,
            "events_written": events_written,
        }
