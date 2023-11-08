from decimal import Decimal

from sqlalchemy import String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BaseDBMixin
import typing

if typing.TYPE_CHECKING:
    from .user import User


class Area(BaseDBMixin, Base):
    name: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(precision=6))
    longtitude: Mapped[Decimal] = mapped_column(DECIMAL(precision=6))
    address: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates='areas')
    rooms: Mapped[typing.List["Room"]] = relationship(back_populates='area')


class Room(BaseDBMixin, Base):
    name: Mapped[str] = mapped_column(String(100))
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))
    area: Mapped["Area"] = relationship(back_populates='rooms')
