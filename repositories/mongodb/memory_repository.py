from datetime import datetime, timezone

from core.config import get_settings
from repositories.mongodb.client import MongoDBClientManager


class MemoryRepository:

    def __init__(self, mongo: MongoDBClientManager):
        settings = get_settings()

        self.db = mongo.client[settings.mongodb_database_name]

        self.long_term_memory = self.db["long_term_memory"]
        self.short_term_memory = self.db["short_term_memory"]

    async def insert_long_term_memory(
        self,
        user_id: str,
        memory: str,
    ) -> None:

        now = datetime.now(timezone.utc)

        await self.long_term_memory.insert_one(
            {
                "user_id": user_id,
                "memory": memory,
                "created_at": now,
                "updated_at": now,
            }
        )

    async def get_long_term_memory(
        self,
        user_id: str,
    ) -> list[dict]:

        cursor = self.long_term_memory.find(
            {
                "user_id": user_id,
            }
        )

        return await cursor.to_list(length=None)

    async def insert_short_term_memory(
        self,
        session_id: str,
        query: str,
        response: str,
    ) -> None:

        await self.short_term_memory.insert_one(
            {
                "session_id": session_id,
                "query": query,
                "response": response,
                "created_at": datetime.now(timezone.utc),
            }
        )

    async def get_short_term_memory(
        self,
        session_id: str,
    ) -> list[dict]:

        cursor = self.short_term_memory.find(
            {
                "session_id": session_id,
            }
        ).sort(
            "created_at",
            1,
        )

        return await cursor.to_list(length=None)
