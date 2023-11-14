import typing
from datetime import date

from pydantic import BaseModel


class BaseUserMixin(BaseModel):
    first_name: typing.Optional[str] = None
    last_name: typing.Optional[str] = None
    phone_number: typing.Optional[str] = None
    sex: typing.Optional[str] = None
    birth_date: typing.Optional[date] = None


class BaseModelMixin(BaseModel):
    pass
