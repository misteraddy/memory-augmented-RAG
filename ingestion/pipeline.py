import uuid
from pathlib import Path

from core.config import get_settings
from ingestion.chunker import TextChunker
from ingestion.document_loader import PDFDocumentLoader
from ingestion.embedder import EmbeddingService
from repositories.qdrant.client import QdrantClientManager
from repositories.qdrant.collection_manager import QdrantCollectionManager
from repositories.qdrant.knowledge_repository import KnowledgeRepository
from utils.ids import generate_chunk_id


settings = get_settings()


class KnowledgeBaseIngestionPipeline:

    def __init__(self, qdrant: QdrantClientManager, collection_name: str):

        self.collection_manager = QdrantCollectionManager(qdrant)

        self.knowledge_repository = KnowledgeRepository(qdrant, collection_name)

        self.loader = PDFDocumentLoader()

        self.chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        self.embedder = EmbeddingService()

    async def ingest_file(
        self,
        file_path: str,
    ) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Unsupported file type: {path.suffix}"
            )

        try:

            # Ensure Qdrant collection
            await self.collection_manager.ensure_collection()

            # Load PDF
            pages = self.loader.load(
                str(path)
            )

            if not pages:
                raise ValueError(
                    "PDF contains no extractable text"
                )

            chunks = self.chunker.chunk_document(
                pages
            )

            if not chunks:
                raise ValueError(
                    "No chunks generated from document"
                )


            texts = [
                chunk["text"]
                for chunk in chunks
            ]

            embeddings = self.embedder.embed_documents(
                texts
            )

            qdrant_chunks = []

            for chunk, embedding in zip(
                chunks,
                embeddings,
            ):

                chunk_index = chunk[
                    "chunk_index"
                ]

                point_id = generate_chunk_id(
                    file_name=path.name,
                    chunk_index=chunk_index,
                )

                metadata = {
                    "file_name": path.name,
                    "page_number": chunk[
                        "page_number"
                    ],
                    "chunk_id": point_id,
                    "chunk_index": chunk_index,
                    "source": "knowledge_base",
                    "text": chunk["text"],
                }

                qdrant_chunks.append(
                    {
                        "point_id": point_id,
                        "embedding": embedding,
                        "metadata": metadata,
                    }
                )

            await self.knowledge_repository.upsert_chunks(
                qdrant_chunks
            )

            return {
                "status": "ingested",
                "file_name": path.name,
                "chunk_count": len(qdrant_chunks),
            }

        except Exception:

            raise