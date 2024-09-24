import enum

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
import sqlalchemy.orm as orm

from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class AchievementType(enum.Enum):
    FIRST_FAVORITE_OFFER = "FIRST_FAVORITE_OFFER"


class Achievement(PcObject, Base, Model):
    __tablename__ = "achievement"

    slug = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=False)

    userAchievements: list["UserAchievement"] = orm.relationship("UserAchievement", back_populates="achievement")


class UserAchievement(PcObject, Base, Model):
    __tablename__ = "user_achievement"

    userId = Column(Integer, ForeignKey(users_models.User.id), nullable=False)
    achievementId = Column(Integer, ForeignKey(Achievement.id), nullable=False)
    completionDate = Column(DateTime, nullable=False)

    user = orm.relationship(users_models.User, back_populates="achievements", foreign_keys=userId)
    achievement = orm.relationship(Achievement, back_populates="userAchievements", foreign_keys=achievementId)

    __table_args__ = (UniqueConstraint("userId", "achievementId", name="user_achievement_unique"),)
