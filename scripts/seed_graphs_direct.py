#!/usr/bin/env python3
"""
Direct Neo4j Graph Seeder — THE MENTALIST
==========================================
Writes entity and relationship nodes directly to Neo4j for the seeded historical cases,
bypassing the LLM extraction pipeline (which requires an API key).

This script reads the case IDs from the API, matches them to historical case definitions,
and calls the Neo4j driver directly.

Usage:
    python scripts/seed_graphs_direct.py

Prerequisites:
    pip install neo4j requests
    Backend + Neo4j running via docker-compose
"""
import sys
import requests

try:
    from neo4j import GraphDatabase
except ImportError:
    print("ERROR: neo4j driver not installed. Run: pip install neo4j")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────
API_BASE      = "http://localhost:8000/api"
DEMO_EMAIL    = "demo@crimenet.local"
DEMO_PASSWORD = "crimenet2026"
NEO4J_URI     = "bolt://localhost:7687"
NEO4J_USER    = "neo4j"
NEO4J_PASS    = "crimenet_neo4j_2026"  # matches .env

# Import definitions from the seeder script
import importlib.util, os
spec = importlib.util.spec_from_file_location(
    "seed_hist",
    os.path.join(os.path.dirname(__file__), "seed_historical_cases.py")
)
seed_mod = importlib.util.module_from_spec(spec)   # type: ignore
spec.loader.exec_module(seed_mod)                  # type: ignore
HISTORICAL_CASES = seed_mod.HISTORICAL_CASES


def get_case_id_map(api_base: str, token: str) -> dict[str, str]:
    """Return {title: case_id} for all cases in the API."""
    r = requests.get(f"{api_base}/cases",
                     headers={"Authorization": f"Bearer {token}"}, timeout=10)
    r.raise_for_status()
    return {c["title"]: c["id"] for c in r.json().get("cases", [])}


def write_case_graph(driver, case_id: str, definition: dict) -> dict:
    nodes_written = 0
    rels_written  = 0

    with driver.session() as session:
        # Write entities
        for entity in definition["entities"]:
            props = {
                "id":               entity["id_slug"],
                "case_id":          case_id,
                "name":             entity["name"],
                "source_document_id": "HISTORICAL_SEED",
                "extracted_by":     "historical_seed_script",
                "evidence_text":    f"Sourced from: {definition['title']} — historical record",
                **entity.get("properties", {}),
            }
            # Flatten any list values to comma-separated strings for Neo4j compat
            safe_props = {}
            for k, v in props.items():
                if isinstance(v, list):
                    safe_props[k] = ", ".join(str(x) for x in v)
                elif v is not None:
                    safe_props[k] = str(v) if not isinstance(v, (int, float, bool)) else v
            label = entity["type"]
            set_parts = ", ".join(f"n.{k} = ${k}" for k in safe_props)
            cypher = (
                f"MERGE (n:{label} {{id: $id, case_id: $case_id}}) "
                f"SET {set_parts}"
            )
            session.run(cypher, safe_props)
            nodes_written += 1

        # Write relationships
        for rel in definition["relationships"]:
            props = {
                "confidence":         rel.get("confidence", 0.95),
                "source_document_id": "HISTORICAL_SEED",
                "evidence_text":      rel.get("evidence", "")[:300],
                "extracted_by":       "historical_seed_script",
                "verified":           "true" if rel.get("verified") else "unverified",
            }
            if rel.get("note"):
                props["note"] = rel["note"]

            from_label = rel["from_type"]
            to_label   = rel["to_type"]
            rel_type   = rel["type"]

            cypher = f"""
            MATCH (a:{from_label} {{id: $from_id, case_id: $case_id}})
            MATCH (b:{to_label}   {{id: $to_id,   case_id: $case_id}})
            MERGE (a)-[r:{rel_type} {{source_document_id: 'HISTORICAL_SEED'}}]->(b)
            SET r += $props
            """
            try:
                session.run(cypher, {
                    "from_id": rel["from"],
                    "to_id":   rel["to"],
                    "case_id": case_id,
                    "props":   props,
                })
                rels_written += 1
            except Exception as e:
                print(f"      Rel error ({rel['from']} → {rel['to']}): {e}")

    return {"nodes": nodes_written, "rels": rels_written}


def main() -> None:
    print("=" * 60)
    print("  THE MENTALIST — Direct Graph Seeder")
    print("  Writes historical entity graphs directly to Neo4j")
    print("=" * 60)

    # Auth
    print("\n[1/3] Authenticating…")
    try:
        r = requests.post(f"{API_BASE}/auth/login",
            json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}, timeout=10)
        r.raise_for_status()
        token = r.json()["access_token"]
        print("  ✓ Authenticated")
    except Exception as e:
        print(f"  ✗ Auth failed: {e}")
        sys.exit(1)

    # Neo4j
    print("[2/3] Connecting to Neo4j…")
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print("  ✓ Neo4j connected")
    except Exception as e:
        print(f"  ✗ Neo4j connection failed: {e}")
        print("  Check NEO4J_URI / credentials in this script match your .env")
        sys.exit(1)

    # Resolve case IDs
    case_id_map = get_case_id_map(API_BASE, token)

    print(f"\n[3/3] Writing graphs for {len(HISTORICAL_CASES)} historical cases…\n")
    total_nodes = 0
    total_rels  = 0

    for defn in HISTORICAL_CASES:
        title    = defn["title"]
        case_id  = case_id_map.get(title)
        if not case_id:
            print(f"  ✗ Not found in API: {title[:55]}")
            print("    Run seed_historical_cases.py first.")
            continue

        print(f"  ▶  {title[:55]}")
        try:
            stats = write_case_graph(driver, case_id, defn)
            total_nodes += stats["nodes"]
            total_rels  += stats["rels"]
            print(f"     ✓ {stats['nodes']} nodes, {stats['rels']} relationships written\n")
        except Exception as e:
            print(f"     ✗ Failed: {e}\n")

    driver.close()

    print(f"Summary: {total_nodes} nodes, {total_rels} relationships written to Neo4j")
    print("\nRefresh any open case in THE MENTALIST to see the investigation network.\n")


if __name__ == "__main__":
    main()
