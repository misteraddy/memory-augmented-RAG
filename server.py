from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.router import api_router
from core.database import DatabaseManager
from repositories.qdrant import collection_manager
from repositories.qdrant.collection_manager import (
    QdrantCollectionManager,
)

from core.config import Settings


database = DatabaseManager()

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):

    await database.connect()

    qdrant_collection_manager = QdrantCollectionManager(
        database.qdrant
    )

    collection_exists = await collection_manager.ensure_collection(
    settings.qdrant_collection_name
    )

    if not collection_exists:
        await collection_manager.create_collection(
            settings.qdrant_collection_name
    )

    await qdrant_collection_manager.ensure_collection(
        settings.qdrant_conversation_collection_name
    )

    conversation_collection_exists = await collection_manager.ensure_collection(
        settings.qdrant_conversation_collection_name
    )

    if not conversation_collection_exists:
        await collection_manager.create_collection(
            settings.qdrant_conversation_collection_name
    )

    yield

    await database.close()


app = FastAPI(
    title="Memory Augmented RAG",
    description="Memory-Augmented RAG backend",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(api_router)


@app.get("/")
async def root():

    return {
        "service": "memory-augmented-rag",
        "status": "running",
    }