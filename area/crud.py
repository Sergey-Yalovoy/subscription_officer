import typing
from decimal import Decimal

from sqlalchemy import select, insert, func
from sqlalchemy.orm import selectinload

from db.session import async_session_maker
from models.area import Area, Room
from graphql_schemas.area import Room as RoomSchema


async def get_area_by_id(area_id: int, user_id: int):
    async with async_session_maker() as session:
        stmt = (
            select(Area)
            .where(Area.id == area_id, Area.user_id == user_id)
            .options(selectinload(Area.rooms))
            .limit(1)
        )
        results = await session.execute(stmt)
    return results.unique().scalar_one_or_none()


async def get_my_areas(
    user_id: int,
    limit: int,
    offset: int,
    keys: typing.Optional[typing.List[int]] = None,
):
    async with async_session_maker() as session:
        stmt = (
            select(Area)
            .filter(Area.user_id == user_id)
            .options(selectinload(Area.rooms))
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).filter(Area.user_id == user_id)
        if keys:
            stmt = stmt.filter(Area.id.in_(keys))
            count_stmt = count_stmt.filter(Area.id.in_(keys))
        results = await session.execute(stmt)
        count = await session.execute(count_stmt)
    return results.scalars().all(), count.scalar_one_or_none()


async def get_my_rooms(user_id: int):
    async with async_session_maker() as session:
        stmt = select(Room).join(Room.area).where(Area.user_id == user_id)
        results = await session.execute(stmt)
    return results.scalars().all()


async def create_room(area_id: int, name: str):
    async with async_session_maker() as session:
        room = Room(name=name, area_id=area_id)
        session.add(room)
        await session.commit()
        await session.refresh(room)
        return room


async def create_rooms(rooms: typing.List[dict]):
    async with async_session_maker() as session:
        stmt = insert(Room).returning(Room)
        result = await session.execute(stmt, rooms)
        await session.commit()
        return result.scalars().all()


async def create_area(
    name: str, latitude: Decimal, longtitude: Decimal, address: str, user_id: int
) -> object:
    async with async_session_maker() as session:
        area = Area(
            name=name,
            latitude=latitude,
            longtitude=longtitude,
            address=address,
            user_id=user_id,
        )
        session.add(area)
        await session.commit()
        await session.refresh(area)
    return area
