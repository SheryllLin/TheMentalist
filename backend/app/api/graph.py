"""
Graph API endpoints — serve Neo4j data to the frontend.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.neo4j import neo4j_session
from app.models.user import User
from app.services.auth import get_current_user
from app.services.graph import GraphService
from app.utils.audit import log_action
from app.utils.case_access import get_case_or_403

router = APIRouter(tags=["graph"])


@router.get("/cases/{case_id}/graph")
async def get_graph(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    data = await GraphService.get_case_graph(neo4j, str(case_id))
    await log_action(db, "GRAPH_VIEW", user_id=current_user.id, case_id=case_id)
    return data


@router.get("/cases/{case_id}/graph/node/{node_id}")
async def get_node(
    case_id: uuid.UUID,
    node_id: str,
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    data = await GraphService.get_node_detail(neo4j, str(case_id), node_id)
    if not data:
        raise HTTPException(status_code=404, detail="Node not found")
    return data


@router.get("/cases/{case_id}/graph/path")
async def shortest_path(
    case_id: uuid.UUID,
    from_id: str = Query(...),
    to_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    path = await GraphService.get_shortest_path(neo4j, str(case_id), from_id, to_id)
    return path


@router.get("/cases/{case_id}/graph/search")
async def search_graph(
    case_id: uuid.UUID,
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    results = await GraphService.search_entities(neo4j, str(case_id), q)
    return {"results": results}


@router.get("/cases/{case_id}/graph/analytics/centrality")
async def degree_centrality(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    results = await GraphService.get_degree_centrality(neo4j, str(case_id))
    return {"centrality": results}


@router.get("/cases/{case_id}/entities")
async def get_entities(
    case_id: uuid.UUID,
    label: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    if label:
        entities = await GraphService.get_entities_by_type(neo4j, str(case_id), label)
    else:
        graph = await GraphService.get_case_graph(neo4j, str(case_id))
        entities = graph["nodes"]
    return {"entities": entities}


@router.get("/cases/{case_id}/timeline")
async def get_timeline(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    await get_case_or_403(db, case_id, current_user)
    events = await GraphService.get_entity_timeline(neo4j, str(case_id))
    return {"events": events}


@router.delete("/cases/{case_id}/graph", status_code=204)
async def delete_case_graph(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    neo4j = Depends(neo4j_session),
    current_user: User = Depends(get_current_user),
):
    """Delete all graph data for a case (e.g., to re-process from scratch)."""
    await get_case_or_403(db, case_id, current_user)
    deleted = await GraphService.delete_case_graph(neo4j, str(case_id))
    await log_action(db, "GRAPH_DELETE", user_id=current_user.id, case_id=case_id,
                     metadata={"nodes_deleted": deleted})
