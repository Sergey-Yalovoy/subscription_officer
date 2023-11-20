import typing
from enum import Enum

from pydantic import BaseModel

from schemas.users_schemas import ShortUserRead


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
    user: typing.Optional[ShortUserRead] = None
    message: str = ""
    online_users: typing.Optional[typing.List[ShortUserRead]] = None
