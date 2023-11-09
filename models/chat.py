import typing
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import BaseDBMixin, Base
from utils.tools import change_case

if typing.TYPE_CHECKING:
    from .user import User


class AssociationChatMembers(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"), primary_key=True)


class Chat(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    messages: Mapped[typing.List["Message"] | None] = relationship(
        back_populates="chat"
    )

    chat_members: Mapped[typing.List["User"]] = relationship(
        secondary="association_chat_members", back_populates="chats"
    )


#     online users id redis db


class Message(BaseDBMixin, Base):
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped[int] = relationship(back_populates="author_messages")
    text: Mapped[str] = mapped_column(String(1000))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))
    chat: Mapped["Chat"] = relationship(back_populates="messages")
