from enum import Enum

from pydantic import BaseModel


class MessageType(str, Enum):
    connect_user: str = "connect"
    disconnect_user: str = "disconnect_user"
    send_message: str = "message"


class UserRole(Enum):
    manager: str = "Manager"
    client: str = "Client"
    worker: str = "Worker"


class WebsocketMessage(BaseModel):
    type: MessageType = MessageType.send_message
    message: str = ""
