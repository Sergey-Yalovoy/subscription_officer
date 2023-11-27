import typing

from area.crud import get_my_areas
from graphql_schemas.area import Area as AreaSchema, Room as RoomSchema
from models.area import Area


async def load_my_areas(
    user_id: int,
    limit: int,
    offset: int,
    keys: typing.Optional[typing.List[int]] = None,
) -> typing.Tuple[typing.List[AreaSchema], int]:
    result = await get_my_areas(user_id, limit, offset, keys)
    areas: typing.List[Area] = result[0]
    count: int = result[1]
    return [
        AreaSchema(
            id=area.id,
            created_at=area.created_at,
            name=area.name,
            latitude=area.latitude,
            longtitude=area.longtitude,
            address=area.address,
            rooms=[
                RoomSchema(id=room.id, created_at=room.created_at, name=room.name)
                for room in area.rooms
            ],
        )
        for area in areas
    ], count
