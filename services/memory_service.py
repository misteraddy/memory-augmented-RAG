from repositories.mongodb import memory_repository
from services.ingestion_service import ingest_semantic_memory
from qdrant_client import models

from core.config import get_settings
from ingestion.embedder import EmbeddingService


async def fetch_long_term_memory(user_id: str):
    return await memory_repository.get_long_term_memory(
        user_id=user_id
    )


async def fetch_short_term_memory(session_id: str):
    return await memory_repository.get_short_term_memory(
        session_id=session_id
    )


async def fetch_semantic_memory(
    qdrant,
    query: str,
    user_id: str,
):
    settings = get_settings()

    embedder = EmbeddingService()

    query_embedding = await embedder.embed_text(query)

    search_result = await qdrant.client.query_points(
        collection_name=settings.qdrant_conversation_collection_name,
        query=query_embedding,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(
                        value=user_id,
                    ),
                )
            ]
        ),
        limit=5,
    )

    semantic_memories = []

    for point in search_result.points:

        content = point.payload.get("content")

        if not content:
            continue

        semantic_memories.append(
            {
                "memory_id": point.payload.get("memory_id"),
                "content": content,
                "score": point.score,
            }
        )

    return semantic_memories


async def save_in_long_term_memory(
    user_id: str,
    query: str,
    response: dict,
):
    long_term_memories = response.get(
        "long_term_memories",
        [],
    )

    if not long_term_memories:
        return

    for memory in long_term_memories:

        if not memory.strip():
            continue

        await memory_repository.insert_long_term_memory(
            user_id=user_id,
            memory=memory,
        )


async def save_in_short_term_memory(
    session_id: str,
    query: str,
    response: str,
):
    await memory_repository.insert_short_term_memory(
        session_id=session_id,
        query=query,
        response=response,
    )


async def save_in_semantic_memory(
    qdrant,
    user_id: str,
    session_id: str,
    response: dict,
):
    semantic_memory = response.get(
        "semantic_memory",
        "",
    ).strip()

    if not semantic_memory:
        return

    await ingest_semantic_memory(
        qdrant=qdrant,
        user_id=user_id,
        session_id=session_id,
        content=semantic_memory,
    )