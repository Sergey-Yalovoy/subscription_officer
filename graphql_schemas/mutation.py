import typing
from decimal import Decimal

import strawberry

from area.crud import create_area, create_room, create_rooms
from graphql_schemas.area import Area as AreaSchema, Room as RoomSchema, RoomInput
from models.area import Area, Room


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_area(
        self, name: str, latitude: Decimal, longtitude: Decimal, address: str
    ) -> AreaSchema:
        user_id: int = 1
        area: Area = await create_area(name, latitude, longtitude, address, user_id)
        area_s = AreaSchema(
            id=area.id,
            created_at=area.created_at,
            name=area.name,
            latitude=area.latitude,
            longtitude=area.longtitude,
            address=area.address,
            rooms=[],
            user_id=user_id,
        )
        return area_s

    @strawberry.mutation
    async def add_room(self, area_id: int, name: str) -> RoomSchema:
        room = await create_room(area_id, name)
        room_s: RoomSchema = RoomSchema(
            id=room.id, created_at=room.created_at, name=room.name, area_id=room.area_id
        )
        return room_s

    @strawberry.mutation
    async def add_rooms(
        self, rooms: typing.List[RoomInput | None]
    ) -> typing.List[RoomSchema]:
        rooms = [room.__dict__ for room in rooms]
        print(rooms)
        rooms_obj: typing.List[Room] = await create_rooms(rooms)
        output_rooms = [
            RoomSchema(
                id=obj.id, created_at=obj.created_at, name=obj.name, area_id=obj.area_id
            )
            for obj in rooms_obj
        ]
        return output_rooms
