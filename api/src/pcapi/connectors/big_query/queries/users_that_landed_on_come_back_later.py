import datetime

import pydantic

from pcapi import settings

from .base import BaseQuery


DEFAULT_DAYS_AGO = 3


class UserThatLandedOnComeBackLaterModel(pydantic.BaseModel):
    user_id: int
    event_date: datetime.date


class UsersThatLandedOnComeBackLater(BaseQuery):
    days_ago: int

    model = UserThatLandedOnComeBackLaterModel

    def __init__(self, days_ago: int = DEFAULT_DAYS_AGO) -> None:
        super().__init__()
        self.days_ago = days_ago

    @property
    def raw_query(self) -> str:
        return f"""
            SELECT
                user_id, event_date
            FROM
                `{settings.BIG_QUERY_NOTIFICATIONS_TABLE_BASENAME}.users_that_landed_on_come_back_later`
            WHERE 
                event_date = DATE_SUB(CURRENT_DATE(), INTERVAL {self.days_ago} DAY)
        """
