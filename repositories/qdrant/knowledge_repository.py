from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    PointStruct,
)

from core.config import get_settings
from repositories.qdrant.client import QdrantClientManager


class KnowledgeRepository:

    def __init__(self, client_manager: QdrantClientManager,collection_name):
        self.client = client_manager.client
        self.collection_name = collection_name

    async def upsert_chunks(
        self,
        chunks: list[dict],
    ) -> None:

        points = [
            PointStruct(
                id=chunk["point_id"],
                vector=chunk["embedding"],
                payload=chunk["metadata"],
            )
            for chunk in chunks
        ]

        if not points:
            return

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def delete_document(
        self,
        file_name: str,
    ) -> None:

        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="file_name",
                        match=MatchValue(
                            value=file_name,
                        ),
                    )
                ]
            ),
        )