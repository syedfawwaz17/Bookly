from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class TagCreateModel(BaseModel):
    name: str


class TagUpdateModel(BaseModel):
    name: Optional[str] = None


class TagModel(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    uid: uuid.UUID
    name: str
    created_at: datetime