from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = Field(
        default="Memory Augmented RAG",
        alias="APP_NAME"
    )

    app_env: str = Field(
        default="development",
        alias="APP_ENV"
    )

    mongodb_uri: str = Field(
        alias="MONGODB_URI"
    )

    mongodb_database: str = Field(
        default="memory_augmented_rag",
        alias="MONGODB_DATABASE"
    )

    qdrant_url: str = Field(
        alias="QDRANT_URL"
    )

    qdrant_api_key: str = Field(
        alias="QDRANT_API_KEY"
    )

    qdrant_collection_name: str = Field(
        default="memory_augmented_knowledge_base",
        alias="QDRANT_COLLECTION_NAME"
    )

    qdrant_conversation_collection_name: str = Field(
        default="conversation_semantic_memory",
        alias="QDRANT_SEMANTIC_MEMORY_COLLECTION"
    )

    embedding_dimension: int = Field(
        default=384,
        alias="EMBEDDING_DIMENSION"
    )

    mongodb_max_pool_size: int = Field(
        default=20,
        alias="MONGODB_MAX_POOL_SIZE"
    )

    mongodb_min_pool_size: int = Field(
        default=2,
        alias="MONGODB_MIN_POOL_SIZE"
    )

    mongodb_server_selection_timeout_ms: int = Field(
        default=5000,
        alias="MONGODB_SERVER_SELECTION_TIMEOUT_MS"
    )

    qdrant_timeout: float = Field(
        default=10.0,
        alias="QDRANT_TIMEOUT"
    )

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL"
    )

    knowledge_base_path: str = Field(
        default="knowledge_base/pdfs",
        alias="KNOWLEDGE_BASE_PATH"
    )

    chunk_size: int = Field(
        default=1000,
        alias="CHUNK_SIZE"
    )

    chunk_overlap: int = Field(
        default=150,
        alias="CHUNK_OVERLAP"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()