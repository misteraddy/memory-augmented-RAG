from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from core.config import get_settings


class MongoDBClient:

    def __init__(self):
        settings = get_settings()

        self.client = AsyncMongoClient(
            settings.mongodb_uri,
            server_api=ServerApi("1"),
            maxPoolSize=settings.mongodb_max_pool_size,
            minPoolSize=settings.mongodb_min_pool_size,
            serverSelectionTimeoutMS=(
                settings.mongodb_server_selection_timeout_ms
            ),
        )

        self.database = self.client[
            settings.mongodb_database
        ]

    async def connect(self) -> None:
        await self.client.admin.command("ping")

    async def close(self) -> None:
        await self.client.close()

    async def health_check(self) -> bool:
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def get_collection(self, collection_name: str):
        return self.database[collection_name]