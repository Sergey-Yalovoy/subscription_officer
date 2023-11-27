from typing import Optional

from fastapi import Request, HTTPException
from fastapi import (
    WebSocket,
    Depends,
    WebSocketException,
    status,
)
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
    CookieTransport,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from config import settings
from graphQL_exception.auth import AuthError
from models.user import User
from models.user import get_user_db
from strawberry.exceptions import MissingQueryError

SECRET = settings.secret


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookies_transport = CookieTransport(cookie_name="authorization")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)


async def get_user_from_headers_websocket(
    websocket: WebSocket, user_manager=Depends(get_user_manager)
):
    token = websocket.headers.get("authorization")
    if "Bearer" in token:
        token = token.split()[-1]
    if not token:
        raise WebSocketException(code=status.HTTP_403_FORBIDDEN, reason="Invalid user")
    user = await auth_backend.get_strategy().read_token(token, user_manager)
    if not user or not user.is_active:
        raise WebSocketException(code=status.HTTP_403_FORBIDDEN, reason="Invalid user")
    yield user


async def read_token_func(token: str, user_manager: UserManager) -> User:
    if not token:
        raise AuthError()
    user = await auth_backend.get_strategy().read_token(token, user_manager)
    if not user or not user.is_active:
        raise AuthError()
    return user
