from google import genai

from core.config import get_settings


client = genai.Client()


async def call_llm(
    final_prompt: str,
) -> str:

    settings = get_settings()

    response = await client.aio.models.generate_content(
        model=settings.model_name,
        contents=final_prompt,
    )

    if not response or not response.text:
        raise RuntimeError("LLM returned an empty response")

    return response.text.strip()