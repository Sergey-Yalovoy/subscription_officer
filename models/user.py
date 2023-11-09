import datetime
from enum import Enum
import typing
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import get_async_session
from .base_model import Base, BaseDBMixin
from .area import Area
from .chat import Chat, Message


class UserRole(Enum):
    manager: str = "Manager"
    client: str = "Client"
    worker: str = "Worker"


class Sex(Enum):
    male: str = "Male"
    female: str = "female"


class User(BaseDBMixin, SQLAlchemyBaseUserTable[int], Base):
    user_role: Mapped[UserRole] = mapped_column(default=UserRole.client)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    phone_number: Mapped[str | None] = mapped_column(String(50))
    sex: Mapped[Sex | None] = mapped_column(String(20))
    birth_date: Mapped[datetime.date | None]
    areas: Mapped[typing.List["Area"]] = relationship(back_populates="user")
    chats: Mapped[typing.List["Chat"]] = relationship(
        secondary="association_chat_members", back_populates="chat_members"
    )
    author_messages: Mapped[typing.List["Message"]] = relationship(
        back_populates="author"
    )


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
