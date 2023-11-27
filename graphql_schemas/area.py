import typing
from decimal import Decimal

import strawberry

from graphql_schemas.base import Base, BaseInput
from graphql_schemas.pagination import LimitOffsetPage


@strawberry.type
class Room(Base):
    name: str


@strawberry.input
class RoomInput(BaseInput):
    name: str
    area_id: int


@strawberry.type
class RoomPage(LimitOffsetPage[Room]):
    pass


@strawberry.type
class Area(Base):
    name: str
    latitude: Decimal
    longtitude: Decimal
    address: str
    rooms: typing.List[Room]


@strawberry.type
class AreaPage(LimitOffsetPage[Area]):
    pass
