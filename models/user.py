import datetime
from enum import Enum

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from db.session import get_async_session
from .base_model import Base, BaseDBMixin


class UserRole(Enum):
    manager: str = 'Manager'
    client: str = 'Client'
    worker: str = 'Worker'


class Sex(Enum):
    male: str = "Male"
    female: str = "female"


class User(BaseDBMixin, SQLAlchemyBaseUserTable[int], Base):
    user_role: Mapped[UserRole] = mapped_column(default=UserRole.client)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    phone_number: Mapped[str | None] = mapped_column(String(50))
    sex: Mapped[Sex] = mapped_column(String(20))
    birth_date: Mapped[datetime.date | None]


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
