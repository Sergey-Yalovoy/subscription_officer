import typing
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from schemas.users_schemas import UserRead, ShortUserRead
from utils.pagiantion import PaginationSchema


class MessageSchema(BaseModel):
    id: int
    created_at: datetime
    author_id: int
    text: str
    chat_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ChatSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    messages: typing.List["MessageSchema"] = []
    chat_members: typing.List["ShortUserRead"] = []


class PaginationChatSchema(PaginationSchema, ChatSchema):
    pass
