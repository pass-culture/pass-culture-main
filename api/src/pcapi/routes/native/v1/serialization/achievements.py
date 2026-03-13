from datetime import datetime

from pydantic import RootModel

from pcapi.core.achievements.models import AchievementEnum
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class MarkAchievementsAsSeenRequest(HttpQueryParamsModel):
    achievement_ids: list[int]


class AchievementResponse(HttpBodyModel):
    id: int
    name: AchievementEnum
    seenDate: datetime | None
    unlockedDate: datetime


class AchievementsResponse(RootModel):
    root: list[AchievementResponse]
