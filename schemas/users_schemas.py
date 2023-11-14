from datetime import datetime

from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr, BaseModel

from .base import BaseUserMixin


class UserRead(schemas.BaseUser[int], BaseUserMixin):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ShortUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr


class UserCreate(schemas.BaseUserCreate, BaseUserMixin):
    pass


class UserUpdate(schemas.BaseUserUpdate, BaseUserMixin):
    pass
