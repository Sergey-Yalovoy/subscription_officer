import typing
from datetime import datetime, date

from fastapi_users import schemas
from pydantic import BaseModel


class BaseUserMixin(BaseModel):
    first_name: typing.Optional[str]
    last_name: typing.Optional[str]
    phone_number: typing.Optional[str]
    sex: typing.Optional[str]
    birth_date: typing.Optional[date]


class UserRead(schemas.BaseUser[int], BaseUserMixin):
    created_at: datetime
    # areas: typing.List
    # chats: typing.List
    # author_messages: typing.List


class UserCreate(schemas.BaseUserCreate, BaseUserMixin):
    pass


class UserUpdate(schemas.BaseUserUpdate, BaseUserMixin):
    pass
