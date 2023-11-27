import typing
import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        if await info.context.user:
            return True
        return False
