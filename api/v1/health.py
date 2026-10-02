from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check(request: Request):

    database = request.app.state.database

    result = await database.health_check()

    if result["healthy"]:
        return {
            "status": "healthy",
            "services": {
                "mongodb": "healthy",
                "qdrant": "healthy",
            },
        }

    return JSONResponse(
        status_code=503,
        content={
            "status": "unhealthy",
            "services": {
                "mongodb": (
                    "healthy"
                    if result["mongodb"]
                    else "unhealthy"
                ),
                "qdrant": (
                    "healthy"
                    if result["qdrant"]
                    else "unhealthy"
                ),
            },
        },
    )