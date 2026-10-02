import asyncio

from repositories.mongodb.client import MongoDBClient
from repositories.qdrant.client import QdrantClientManager


class DatabaseManager:

    def __init__(self):
        self.mongodb = MongoDBClient()
        self.qdrant = QdrantClientManager()
        self.qdrant_conversation = QdrantClientManager()

    async def connect(self) -> None:
        await asyncio.gather(
            self.mongodb.connect(),
            self.qdrant.connect(),
            self.qdrant_conversation.connect()
        )

    async def close(self) -> None:
        await asyncio.gather(
            self.mongodb.close(),
            self.qdrant.close(),
            self.qdrant_conversation.close()
        )

    async def health_check(self) -> dict:

        mongodb_health, qdrant_health, qdrant_conversation_health = await asyncio.gather(
            self.mongodb.health_check(),
            self.qdrant.health_check(),
            self.qdrant_conversation.health_check()
        )

        return {
            "mongodb": mongodb_health,
            "qdrant": qdrant_health,
            "qdrant_conversation": self.qdrant_conversation_health,
            "healthy": (
                mongodb_health and qdrant_health and qdrant_conversation_health
            ),
        }