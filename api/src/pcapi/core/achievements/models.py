from datetime import datetime
import enum
import typing

import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import func
from sqlalchemy import orm

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
import pcapi.utils.db as db_utils


if typing.TYPE_CHECKING:
    from pcapi.core.bookings.models import Booking
    from pcapi.core.users.models import User


class AchievementEnum(enum.Enum):
    FIRST_MOVIE_BOOKING = "FIRST_MOVIE_BOOKING"
    FIRST_BOOK_BOOKING = "FIRST_BOOK_BOOKING"
    FIRST_RECORDED_MUSIC_BOOKING = "FIRST_RECORDED_MUSIC_BOOKING"
    FIRST_SHOW_BOOKING = "FIRST_SHOW_BOOKING"
    FIRST_MUSEUM_BOOKING = "FIRST_MUSEUM_BOOKING"
    FIRST_LIVE_MUSIC_BOOKING = "FIRST_LIVE_MUSIC_BOOKING"
    FIRST_NEWS_BOOKING = "FIRST_NEWS_BOOKING"
    FIRST_INSTRUMENT_BOOKING = "FIRST_INSTRUMENT_BOOKING"
    FIRST_ART_LESSON_BOOKING = "FIRST_ART_LESSON_BOOKING"


class Achievement(PcObject, Base, Model):
    __tablename__ = "achievement"

    userId: int = Column(sa.BigInteger, ForeignKey("user.id"), index=True, nullable=False)
    user: orm.Mapped["User"] = orm.relationship("User", foreign_keys=[userId], backref="achievements")

    bookingId: int = Column(sa.BigInteger, ForeignKey("booking.id"), nullable=False)
    booking: orm.Mapped["Booking"] = orm.relationship("Booking", foreign_keys=[bookingId], backref="achievements")

    name: AchievementEnum = Column(db_utils.MagicEnum(AchievementEnum), nullable=False)
    unlockedDate: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    # For when the user has seen the achievement success modal in the native app:
    seenDate: datetime = Column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("userId", "name", name="user_achievement_unique"),)
