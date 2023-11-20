import typing
from uuid import UUID

from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    APIRouter,
    Depends,
    WebSocketException,
    status,
    Body,
    HTTPException,
)
from fastapi_pagination import LimitOffsetPage
from fastapi_users.exceptions import UserNotExists
import json

from auth.auth import get_user_manager, auth_backend, current_active_user, UserManager
from models.chat import Chat, Message
from models.user import User
from schemas.channel_messages import WebsocketMessage, MessageType
from schemas.chat_schemas import ChatSchema, MessageSchema
from schemas.users_schemas import ShortUserRead
from .crud import (
    get_chat_from_db,
    get_chats_by_user_id,
    create_chat_in_db,
    get_chat_with_message,
    get_chat_uuid_by_users,
    get_messages_from_db,
    check_access_to_chat,
    create_message,
)

router = APIRouter(prefix="/chat", tags=["chat"])


async def get_user_from_headers(
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
    print(user.is_active)
    yield user


async def get_user_from_cookies(
    websocket: WebSocket, user_manager=Depends(get_user_manager)
):
    token = websocket.cookies.get("authorization")
    if not token:
        raise WebSocketException(code=status.HTTP_403_FORBIDDEN, reason="Invalid user")
    user = await auth_backend.get_strategy().read_token(token, user_manager)
    if not user or not user.is_active:
        raise WebSocketException(code=status.HTTP_403_FORBIDDEN, reason="Invalid user")
    yield user


class ConnectionManager:
    def __init__(self):
        self.active_connections: typing.Dict[UUID, typing.List[WebSocket]] = {}
        self.online_users: typing.Dict[UUID, typing.Set[User]] = {}

    async def connect(self, websocket: WebSocket, chat_id: UUID, user: User):
        if not await check_access_to_chat(chat_id, user.id):
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION, reason="Can`t access to chat"
            )
        chat: Chat = await get_chat_from_db(chat_id)
        if not chat:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Chat by chat_id is not found",
            )
        await websocket.accept()
        connections = self.active_connections.get(chat_id)
        online_users = self.online_users.get(chat_id)
        if connections is not None:
            connections.append(websocket)
            online_users.add(user)
        else:
            self.active_connections[chat_id] = [websocket]
            self.online_users[chat_id] = set()
            self.online_users[chat_id].add(user)
        await self.send_in_group(
            WebsocketMessage(
                message=f"User {user.email} connect in chat #{chat_id}",
                user=ShortUserRead.model_validate(user),
                type=MessageType.connect_user,
                online_users=[
                    ShortUserRead.model_validate(u) for u in self.online_users[chat_id]
                ],
            ).model_dump_json(),
            chat_id,
        )

    async def disconnect(self, websocket: WebSocket, chat_id: UUID, user: User):
        self.active_connections[chat_id].remove(websocket)
        self.online_users[chat_id].remove(user)
        await self.send_in_group(
            WebsocketMessage(
                message=f"User {user.email} disconnect from chat #{chat_id}",
                user=ShortUserRead.model_validate(user),
                type=MessageType.disconnect_user,
                online_users=[
                    ShortUserRead.model_validate(u) for u in self.online_users[chat_id]
                ],
            ).model_dump_json(),
            chat_id,
        )

    async def send_message(self, message: json, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_in_group(self, message: json, chat_id: UUID):
        connections: typing.List[WebSocket] = self.active_connections.get(chat_id)
        if not connections:
            return
        for connection in connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.get("/", response_model=LimitOffsetPage[ChatSchema])
async def get_chats(user: User = Depends(current_active_user)):
    return await get_chats_by_user_id(user_id=user.id)


@router.get("/{chat_id}", response_model=ChatSchema)
async def get_chat(
    chat_id: UUID, message_limit: int = 1, user: User = Depends(current_active_user)
):
    if not await check_access_to_chat(chat_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not access to chat"
        )
    result = await get_chat_with_message(chat_id, message_limit)
    return ChatSchema.model_validate(result).model_dump()


@router.get("/{chat_id}/messages", response_model=LimitOffsetPage[MessageSchema])
async def get_messages(chat_id: UUID, user: User = Depends(current_active_user)):
    chat: bool = await check_access_to_chat(chat_id, user_id=user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Chat is not found"
        )
    return await get_messages_from_db(chat_id)


@router.post("/", response_model=ChatSchema)
async def create_chat(
    to_user_id: typing.Annotated[int, Body(embed=True)],
    user: User = Depends(current_active_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    check_if_exist_uuid = await get_chat_uuid_by_users(user.id, to_user_id)
    if check_if_exist_uuid:
        result = await get_chat_with_message(check_if_exist_uuid)
        return ChatSchema.model_validate(result).model_dump()
    try:
        await user_manager.get(to_user_id)
    except UserNotExists:
        raise HTTPException(status_code=400, detail="to_user not found")
    result = await create_chat_in_db(user.id, to_user_id)
    return ChatSchema.model_validate(result).model_dump()


@router.websocket("/ws/{chat_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket, chat_id: UUID, user: User = Depends(get_user_from_headers)
):
    await manager.connect(websocket, chat_id, user)
    try:
        while True:
            data: str = await websocket.receive_text()
            if not data:
                continue
            data: dict = json.loads(data)
            websocket_message = WebsocketMessage(**data)
            if not websocket_message.type == MessageType.send_message:
                continue
            message = await create_message(chat_id, user.id, websocket_message.message)
            if message:
                await manager.send_in_group(
                    MessageSchema.model_validate(message).model_dump_json(), chat_id
                )
    except WebSocketDisconnect:
        await manager.disconnect(websocket, chat_id, user)
