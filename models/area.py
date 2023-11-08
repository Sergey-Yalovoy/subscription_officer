import datetime
from decimal import Decimal
from enum import Enum
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import String, DECIMAL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from db.session import get_async_session
from .base_model import Base, BaseDBMixin


class Area(BaseDBMixin, Base):
    name: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(precision=6))
    longtitude: Mapped[Decimal] = mapped_column(DECIMAL(precision=6))
    address: Mapped[str] = mapped_column(String(200))


