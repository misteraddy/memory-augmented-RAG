from qdrant_client import models

from core.config import get_settings
from repositories.qdrant.client import QdrantClientManager


class QdrantCollectionManager:

    def __init__(self, qdrant: QdrantClientManager):
        self.qdrant = qdrant
        self.settings = get_settings()

    async def create_collection(
        self,
        collection_name: str,
    ) -> None:

        await self.qdrant.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=self.settings.embedding_dimension,
                distance=models.Distance.COSINE,
            ),
        )

    async def ensure_collection(
        self,
        collection_name: str,
    ) -> bool:

        return await self.qdrant.client.collection_exists(
            collection_name=collection_name,
        )