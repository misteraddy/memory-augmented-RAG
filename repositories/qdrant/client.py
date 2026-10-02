from qdrant_client import AsyncQdrantClient

from core.config import get_settings


class QdrantClientManager:

    def __init__(self):
        settings = get_settings()

        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=settings.qdrant_timeout,
        )

    async def connect(self) -> None:
        await self.client.get_collections()

    async def close(self) -> None:
        await self.client.close()

    async def health_check(self) -> bool:
        try:
            await self.client.get_collections()
            return True
        except Exception:
            return False