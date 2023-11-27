import typing

import strawberry

from area.crud import get_my_areas
from graphql_schemas.area import AreaPage, Area as AreaSchema
from graphql_schemas.base import LimitOffsetInput
from graphql_schemas.context import Info
from graphql_schemas.user import UserQL
from loaders.area import load_my_areas
from models.area import Area
from permissions.auth import IsAuthenticated


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def areas(
        self,
        pagination: LimitOffsetInput,
        info: Info,
        keys: typing.Optional[typing.List[int]] = None,
    ) -> AreaPage:
        user: UserQL | None = await info.context.user
        areas, count = await load_my_areas(
            user.id, pagination.limit, pagination.offset, keys
        )
        return AreaPage(
            limit=pagination.limit,
            offset=pagination.offset,
            count=count,
            items=areas,
        )

    # @strawberry.field
    # async def rooms(self):
    #     return []
