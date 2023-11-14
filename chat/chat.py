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
from fastapi.templating import Jinja2Templates
from fastapi_users.exceptions import UserNotExists
from pydantic import json

from auth.auth import get_user_manager, auth_backend, current_active_user, UserManager
from .crud import (
    get_chat,
    get_chats_by_user_id,
    create_chat_in_db,
    get_chat_with_message,
    get_chat_uuid_by_users,
)
from models.chat import Chat
from models.user import User
from schemas.channel_messages import WebsocketMessage, MessageType
from schemas.chat_schemas import ChatSchema

router = APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory="templates")


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
        self.online_users: typing.Dict[UUID, typing.List[User]] = {}

    async def connect(self, websocket: WebSocket, chat_id: UUID, user: User):
        chat: Chat = await get_chat(chat_id)
        if not chat:
            raise WebSocketException(
                code=status.HTTP_400_BAD_REQUEST, reason="Chat by chat_id is not found"
            )
        print(chat.chat_members)
        await websocket.accept()
        connections = self.active_connections.get(chat_id)
        online_users = self.online_users.get(chat_id)
        if connections is not None:
            connections.append(websocket)
            online_users.append(user)
        else:
            self.active_connections[chat_id] = [websocket]
            self.online_users[chat_id] = [user]
        await self.send_in_group(
            WebsocketMessage(
                message=f"User {user.email} connect in chat #{chat_id}",
                type=MessageType.connect_user,
            ),
            chat_id,
        )

    async def disconnect(self, websocket: WebSocket, chat_id: UUID, user: User):
        self.active_connections[chat_id].remove(websocket)
        self.online_users[chat_id].remove(user)
        await self.send_in_group(
            WebsocketMessage(
                message=f"User {user.email} connect in chat #{chat_id}",
                type=MessageType.connect_user,
            ),
            chat_id,
        )

    async def send_message_in_group(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_in_group(self, message: json, chat_id: UUID):
        connections: typing.List[WebSocket] = self.active_connections.get(chat_id)
        if not connections:
            return
        for connection in connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.get("/", response_model=typing.List[ChatSchema])
async def get_chats(user: User = Depends(current_active_user)):
    results = await get_chats_by_user_id(user_id=user.id)
    return [ChatSchema.model_validate(result).model_dump() for result in results]


@router.post("/", response_model=typing.List[ChatSchema])
async def create_chat(
    to_user_id: typing.Annotated[int, Body()],
    user: User = Depends(current_active_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    check_if_exist_uuid = await get_chat_uuid_by_users(user.id, to_user_id)
    if check_if_exist_uuid:
        result = await get_chat_with_message(check_if_exist_uuid)
        return [ChatSchema.model_validate(result).model_dump()]
    try:
        await user_manager.get(to_user_id)
    except UserNotExists:
        raise HTTPException(status_code=400, detail="to_user not found")
    results = await create_chat_in_db(user.id, to_user_id)
    return [ChatSchema.model_validate(result).model_dump() for result in results]


@router.websocket("/ws/{chat_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket, chat_id: UUID, user: User = Depends(get_user_from_headers)
):
    await manager.connect(websocket, chat_id, user)
    try:
        while True:
            data = await websocket.receive_text()
            # block save messages
            print("data")
            print(data)
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket, chat_id, user)
