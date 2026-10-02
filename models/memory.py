from datetime import datetime
from pydantic import BaseModel, Field


class LongTermMemoryModel(BaseModel):
    user_id: str
    memory: str
    created_at: datetime
    updated_at: datetime | None = None


class ShortTermMemoryModel(BaseModel):
    session_id: str
    query: str
    response: str
    created_at: datetime

