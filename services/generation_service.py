from services import memory_service
from llm.client import call_llm
from prompt_library import prompt
from repositories.qdrant.client import QdrantClientManager


async def generate_llm_response(
    qdrant:QdrantClientManager,
    query: str,
    user_id: str,
    session_id: str,
    search_results: list,
) -> str:

    try:

        # Fetch long-term memory
        long_term_memory_context = (
            await memory_service.fetch_long_term_memory(
                user_id=user_id
            )
        )

        # Fetch short-term memory
        short_term_memory_context = (
            await memory_service.fetch_short_term_memory(
                session_id=session_id
            )
        )

        # Fetch semantically similar memories
        semantic_memory_context = (
            await memory_service.fetch_semantic_memory(
                qdrant=qdrant,
                query=query,
                user_id=user_id,
            )
        )

        # Build final prompt
        final_prompt = prompt.LLM_PROMPT.format(
            query=query,
            long_term_memory_context=long_term_memory_context,
            short_term_memory_context=short_term_memory_context,
            semantic_memory_context=semantic_memory_context,
            knowledge_context=search_results,
        )

        # Call LLM
        response = await call_llm(
            final_prompt=final_prompt
        )

        return response

    except Exception as e:

        raise RuntimeError(
            f"Failed to generate LLM response: {str(e)}"
        ) from e