from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.config import get_settings
from repositories.qdrant.client import QdrantClientManager
from services import retrieval_service


router = APIRouter(
    prefix="/sessions",
    tags=["Query"],
)


class UserRequestBody(BaseModel):
    user_id: str
    memory_id: str
    query: str


@router.post("/{session_id}")
async def user_rag_query(
    session_id: str = Path(
        ...,
        description="The unique ID of the session",
    ),
    body: UserRequestBody = None,
):
    qdrant = QdrantClientManager()

    result = await retrieval_service.start_retrieval_process(
        qdrant=qdrant,
        query=body.query,
        user_id=body.user_id,
        session_id=session_id,
        memory_id=body.memory_id,
    )

    return JSONResponse(
        status_code=result["status_code"],
        content=result,
    )