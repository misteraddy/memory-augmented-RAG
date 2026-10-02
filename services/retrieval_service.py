from qdrant_client import models

from core.config import get_settings
from ingestion.embedder import EmbeddingService
from repositories.qdrant.client import QdrantClientManager
from repositories.qdrant.collection_manager import QdrantCollectionManager
from services import generation_service
from services import memory_service


async def start_retrieval_process(
    qdrant: QdrantClientManager,
    query: str,
    user_id: str,
    session_id: str,
    memory_id: str | None = None,
):

    if not user_id:
        return {
            "status_code": 400,
            "message": "user_id is mandatory",
        }

    if not session_id:
        return {
            "status_code": 400,
            "message": "session_id is mandatory",
        }

    if not query:
        return {
            "status_code": 400,
            "message": "query is mandatory",
        }

    settings = get_settings()

    embedding_service = EmbeddingService()

    query_embedding = embedding_service.embed_query(
        query
    )

    collection_manager = QdrantCollectionManager(qdrant)

    collection_exists = (
        await collection_manager.collection_exists(
            settings.qdrant_collection_name
        )
    )

    if not collection_exists:
        return {
            "status_code": 404,
            "message": "Knowledge base collection does not exist",
        }


    query_filter = None


    search_result = await qdrant.client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_embedding,
        query_filter=query_filter,
        limit=5,
    )

    llm_response = (
        await generation_service.generate_llm_response(
            qdrant=qdrant,
            query=query,
            user_id=user_id,
            session_id=session_id,
            search_results=search_result,
        )
    )

    await memory_service.save_in_short_term_memory(
        session_id=session_id,
        query=query,
        response=llm_response,
    )

    await memory_service.save_in_long_term_memory(
        user_id=user_id,
        query=query,
        response=llm_response,
    )


    await memory_service.save_in_semantic_memory(
        user_id=user_id,
        session_id=session_id,
        query=query,
        response=llm_response,
    )


    return {
        "status_code": 200,
        "query": query,
        "response": llm_response,
    }