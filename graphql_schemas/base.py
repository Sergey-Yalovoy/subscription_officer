import typing
from datetime import datetime

import strawberry


@strawberry.type
class Base:
    id: int
    created_at: datetime


@strawberry.input
class BaseInput:
    pass


@strawberry.input
class LimitOffsetInput:
    limit: typing.Optional[int]
    offset: typing.Optional[int]
