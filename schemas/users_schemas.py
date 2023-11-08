from datetime import datetime

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    created_at: datetime


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
