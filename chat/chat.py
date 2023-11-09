import typing
from email.policy import HTTP
from uuid import UUID
from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    APIRouter,
    Request,
    Depends,
    WebSocketException,
    status,
)
from fastapi.templating import Jinja2Templates

from auth.auth import get_user_manager, auth_backend

from models.user import User

router = APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory="templates")


async def get_user_from_headers(
    websocket: WebSocket, user_manager=Depends(get_user_manager)
):
    token = websocket.headers.get("authorization")
    if "Bearer" in token:
        token = token.split()[-1]
    print(token)
    if not token:
        raise WebSocketException(code=status.HTTP_403_FORBIDDEN, reason="Invalid user")
    user = await auth_backend.get_strategy().read_token(token, user_manager)
    if not user or not user.is_active:
        raise WebSocketException(code=status.HTTP_403_FORBIDDEN, reason="Invalid user")
    yield user


class ConnectionManager:
    def __init__(self):
        self.active_connections: typing.Dict[UUID, typing.List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: UUID):
        await websocket.accept()
        connections = self.active_connections.get(chat_id)
        if connections is not None:
            connections.append(websocket)
        else:
            self.active_connections[chat_id] = [websocket]

    def disconnect(self, websocket: WebSocket, chat_id: UUID):
        self.active_connections[chat_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_group(self, message: str, chat_id: UUID):
        connections: typing.List[WebSocket] = self.active_connections.get(chat_id)
        if not connections:
            return
        for connection in connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.get("/")
async def chat_render(request: Request):
    return templates.TemplateResponse("chat_page.html", {"request": request})


@router.websocket("/ws/{chat_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket, chat_id: UUID, user: User = Depends(get_user_from_headers)
):
    print(user)
    await manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            print("data")
            print(data)
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)
        await manager.send_group(f"Chat #{chat_id} is close", chat_id)
