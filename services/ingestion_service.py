from datetime import datetime, timezone
from uuid import uuid4

from core.config import get_settings
from ingestion.embedder import EmbeddingService
from repositories.qdrant.client import QdrantClientManager
from repositories.qdrant.collection_manager import (
    QdrantCollectionManager,
)


async def ingest_semantic_memory(
    qdrant: QdrantClientManager,
    user_id: str,
    session_id: str,
    content: str,
) -> None:

    settings = get_settings()

    collection_manager = QdrantCollectionManager(qdrant)

    collection_exists = await collection_manager.collection_exists(
        settings.qdrant_conversation_collection_name
    )

    if not collection_exists:
        await collection_manager.create_collection(
            settings.qdrant_conversation_collection_name
        )

    embedder = EmbeddingService()

    embedding = await embedder.embed_text(content)

    memory_id = str(uuid4())

    point = {
        "id": memory_id,
        "vector": embedding,
        "payload": {
            "memory_id": memory_id,
            "user_id": user_id,
            "session_id": session_id,
            "content": content,
            "timestamp": datetime.now(timezone.utc),
            "source": "semantic_memory",
        },
    }

    await qdrant.client.upsert(
        collection_name=settings.qdrant_conversation_collection_name,
        points=[point],
    )