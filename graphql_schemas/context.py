import asyncstdlib
from strawberry.fastapi import BaseContext
from strawberry.types.info import RootValueType

from auth.auth import read_token_func, UserManager
from graphQL_exception.auth import AuthError
from graphql_schemas.user import UserQL
from models.user import User
from strawberry.types import Info as _Info


class Context(BaseContext):
    def __init__(self, user_manager: UserManager):
        super().__init__()
        self.user_manager = user_manager

    @asyncstdlib.cached_property
    async def user(self) -> UserQL | None:
        if not self.request:
            return None

        authorization: str = self.request.headers.get("Authorization", None)
        try:
            user_obj: User = await read_token_func(authorization, self.user_manager)
        except AuthError:
            return None
        return UserQL(id=user_obj.id)


Info = _Info[Context, RootValueType]
