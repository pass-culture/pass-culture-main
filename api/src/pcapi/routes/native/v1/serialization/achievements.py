from datetime import datetime

from pcapi.core.achievements.models import AchievementEnum
from pcapi.routes.serialization import ConfiguredBaseModel


class MarkAchievementsAsSeenRequest(ConfiguredBaseModel):
    achievement_ids: list[int]


class AchievementResponse(ConfiguredBaseModel):
    id: int
    name: AchievementEnum
    seenDate: datetime | None
    unlockedDate: datetime


class AchievementsResponse(ConfiguredBaseModel):
    __root__: list[AchievementResponse]
