import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.config import get_settings
from ingestion.pipeline import KnowledgeBaseIngestionPipeline
from repositories.qdrant.client import QdrantClientManager


settings = get_settings()


async def main():

    pdf_directory = Path(
        settings.knowledge_base_path
    )

    if not pdf_directory.exists():
        raise FileNotFoundError(
            f"Knowledge base directory does not exist: "
            f"{pdf_directory}"
        )

    pdf_files = list(
        pdf_directory.glob("*.pdf")
    )

    if not pdf_files:
        print("No PDF files found.")
        return

    collection_name = settings.qdrant_collection_name

    qdrant = QdrantClientManager()
    pipeline = KnowledgeBaseIngestionPipeline(qdrant, collection_name)

    try:
        await qdrant.connect()

        for pdf_file in pdf_files:

            print(
                f"\nProcessing: {pdf_file.name}"
            )

            try:
                result = await pipeline.ingest_file(
                    str(pdf_file)
                )

                print(result)

            except Exception as exc:
                print(
                    f"Failed: {pdf_file.name}"
                )

                print(exc)
    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())