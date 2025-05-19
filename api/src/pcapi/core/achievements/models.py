import enum
import typing
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.utils.db as db_utils
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


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

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)
    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[userId], backref="achievements")

    bookingId: int = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), nullable=False)
    booking: sa_orm.Mapped["Booking"] = sa_orm.relationship("Booking", foreign_keys=[bookingId], backref="achievements")

    name: AchievementEnum = sa.Column(db_utils.MagicEnum(AchievementEnum), nullable=False)
    unlockedDate: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now()
    )
    # For when the user has seen the achievement success modal in the native app:
    seenDate: datetime = sa.Column(sa.DateTime, nullable=True)

    __table_args__ = (sa.UniqueConstraint("userId", "name", name="user_achievement_unique"),)
