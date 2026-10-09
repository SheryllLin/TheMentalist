"""
Neo4j async driver wrapper.
Provides a session factory and a FastAPI dependency.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from neo4j import AsyncGraphDatabase, AsyncDriver

from app.config import get_settings

settings = get_settings()

_driver: AsyncDriver | None = None


def get_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_pool_size=50,
        )
    return _driver


async def close_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


@asynccontextmanager
async def get_neo4j_session():
    """Async context manager for a Neo4j session."""
    driver = get_driver()
    async with driver.session() as session:
        yield session


async def neo4j_session() -> AsyncGenerator:
    """FastAPI dependency for Neo4j session."""
    async with get_neo4j_session() as session:
        yield session


async def ensure_constraints() -> None:
    """
    Create Neo4j uniqueness constraints and indexes on first startup.
    Safe to call multiple times (IF NOT EXISTS).
    """
    constraints = [
        # Uniqueness constraints
        "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (n:Person) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT org_id IF NOT EXISTS FOR (n:Organization) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (n:Location) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT phone_id IF NOT EXISTS FOR (n:Phone) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT vehicle_id IF NOT EXISTS FOR (n:Vehicle) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT bank_account_id IF NOT EXISTS FOR (n:BankAccount) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (n:Transaction) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (n:Event) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (n:Document) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT social_id IF NOT EXISTS FOR (n:SocialMediaAccount) REQUIRE n.id IS UNIQUE",
        # Full-text indexes for search
        "CREATE FULLTEXT INDEX entity_name_ft IF NOT EXISTS FOR (n:Person|Organization|Location) ON EACH [n.name]",
    ]
    async with get_neo4j_session() as session:
        for cypher in constraints:
            try:
                await session.run(cypher)
            except Exception as e:
                # Constraint already exists or non-fatal
                pass
