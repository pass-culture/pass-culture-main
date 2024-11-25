from datetime import datetime
import enum

import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import func
from sqlalchemy import orm

from pcapi.core.bookings import models as bookings_models
from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
import pcapi.utils.db as db_utils


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
    user: orm.Mapped["users_models.User"] = orm.relationship(
        "users_models.User", back_populates="achievements", foreign_keys=[userId]
    )

    bookingId: int = Column(sa.BigInteger, ForeignKey("booking.id"), nullable=False)
    booking: orm.Mapped["bookings_models.Booking"] = orm.relationship(
        "bookings_models.Booking", back_populates="achievements", foreign_keys=[bookingId]
    )

    name: AchievementEnum = Column(db_utils.MagicEnum(AchievementEnum), nullable=False)
    unlockedDate: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    # For when the user has seen the achievement success modal in the native app:
    seenDate: datetime = Column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("userId", "name", name="user_achievement_unique"),)
