import typing
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from schemas.users_schemas import UserRead, ShortUserRead


class MessageSchema(BaseModel):
    id: int
    created_at: datetime
    author_id: int
    text: str
    chat_id: int

    model_config = ConfigDict(from_attributes=True)


class ChatSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    messages: typing.List["MessageSchema"] = []
    chat_members: typing.List["ShortUserRead"] = []
