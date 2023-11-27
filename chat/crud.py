from uuid import UUID

from sqlalchemy import select, insert, and_
from sqlalchemy.orm import selectinload, subqueryload, contains_eager

from db.session import async_session_maker
from models.chat import Chat, AssociationChatMembers, Message
from fastapi_pagination.ext.sqlalchemy import paginate

from models.user import User


async def get_chat_from_db(chat_id: UUID):
    async with async_session_maker() as session:
        stmt = (
            select(Chat)
            .where(Chat.id == chat_id)
            .options(selectinload(Chat.chat_members))
        )
        results = await session.execute(stmt)
    return results.unique().scalar_one_or_none()


async def check_access_to_chat(chat_id: UUID, user_id: int):
    async with async_session_maker() as session:
        stmt = (
            select(AssociationChatMembers.chat_id)
            .filter_by(chat_id=chat_id, user_id=user_id)
            .limit(1)
        )
        result = await session.execute(stmt)
        obj = result.unique().scalar_one_or_none()
        if obj:
            return True
        return False


async def get_chat_with_message(chat_id: UUID, default_message_limit: int = 1):
    async with async_session_maker() as session:
        sbq_messages = (
            select(Message.id)
            .where(Message.chat_id == Chat.id)
            .order_by(Message.created_at.desc())
            .limit(default_message_limit)
            .scalar_subquery()
            .correlate(Chat)
        )
        stmt = (
            select(Chat)
            .join(Chat.chat_members)
            .filter(Chat.id == chat_id)
            .outerjoin(Message, Message.id.in_(sbq_messages))
            .options(contains_eager(Chat.messages))
            .options(contains_eager(Chat.chat_members).load_only(User.id, User.email))
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
        return await paginate(session, stmt)


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
            .limit(1)
        )
        return results.unique().scalar_one_or_none()


async def create_message(chat_id: UUID, author_id: int, text: str):
    message = Message(chat_id=chat_id, author_id=author_id, text=text)
    async with async_session_maker() as session:
        session.add(message)
        await session.commit()
        await session.refresh(message)
    return message


async def get_messages_from_db(chat_id: UUID):
    async with async_session_maker() as session:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
        )
        return await paginate(session, stmt)
