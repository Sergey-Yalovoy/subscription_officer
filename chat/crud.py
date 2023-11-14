import typing
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.session import get_async_session, async_session_maker
from models.chat import Chat, AssociationChatMembers


async def get_chat(chat_id: UUID):
    async with async_session_maker() as session:
        stmt = select(Chat).where(Chat.id == chat_id)
        results = await session.execute(stmt)
    return results.unique().scalar_one_or_none()


async def get_chat_with_message(chat_id: UUID):
    async with async_session_maker() as session:
        stmt = (
            select(Chat)
            .options(selectinload(Chat.messages), selectinload(Chat.chat_members))
            .where(Chat.id == chat_id)
        )
        results = await session.execute(stmt)
    return results.unique().scalar_one_or_none()


async def get_chats_by_user_id(user_id: int):
    async with async_session_maker() as session:
        stmt = (
            select(Chat)
            .options(selectinload(Chat.chat_members), selectinload(Chat.messages))
            .where(AssociationChatMembers.user_id == user_id)
        )
        result = await session.execute(stmt)
    return result.scalars().all()


async def get_chat_uuid_by_users(from_user_id: int, to_user_id: int) -> UUID:
    async with async_session_maker() as session:
        sbq = (
            select(AssociationChatMembers.chat_id)
            .where(AssociationChatMembers.user_id == to_user_id)
            .subquery()
        )

        stmt = (
            select(AssociationChatMembers.chat_id)
            .where(
                and_(
                    AssociationChatMembers.user_id == from_user_id,
                    AssociationChatMembers.chat_id.in_(sbq),
                )
            )
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def create_chat_in_db(from_user_id: int, to_user_id: int):
    # не создавать чат с несуществующим пользователем
    users = [from_user_id, to_user_id]
    async with async_session_maker() as session:
        chat = Chat()
        session.add(chat)
        await session.flush()
        await session.refresh(chat)
        chat_members = [{"user_id": user, "chat_id": chat.id} for user in users]
        await session.execute(insert(AssociationChatMembers), chat_members)
        await session.commit()
        results = await session.execute(
            select(Chat)
            .options(selectinload(Chat.chat_members), selectinload(Chat.messages))
            .where(Chat.id == chat.id)
        )
        return results.scalars().all()
