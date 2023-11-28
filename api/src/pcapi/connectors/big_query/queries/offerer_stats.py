import datetime
import typing

import pydantic.v1 as pydantic_v1

from pcapi import settings

from .base import BaseQuery
from .base import RowIterator


DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE = "stats_display_cum_daily_consult_per_offerer_last_180_days"
TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE = "stats_display_top_3_most_consulted_offers_last_30_days"


class OffererViewsModel(pydantic_v1.BaseModel):
    eventDate: datetime.date
    numberOfViews: int


class OffererViewsPerDay(BaseQuery):
    @property
    def raw_query(self) -> str:
        return f"""
        SELECT
            event_date as eventDate,
            cum_consult as numberOfViews
        FROM
            `{settings.BIG_QUERY_NOTIFICATIONS_TABLE_BASENAME}.{DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE}`
        WHERE
            offerer_id = @offerer_id
        ORDER BY event_date DESC
        LIMIT 180
        """

    model = OffererViewsModel

    def execute(self, page_size: int = 180, **parameters: typing.Any) -> RowIterator:
        for row in super().execute(page_size=page_size, **parameters):
            yield OffererViewsModel(
                eventDate=datetime.date.fromisoformat(str(row.eventDate)), numberOfViews=row.numberOfViews
            )


class TopOffersData(pydantic_v1.BaseModel):
    offerId: int
    numberOfViews: int


class OffersData(BaseQuery):
    @property
    def raw_query(self) -> str:
        # FIXME(ghaliela, 2023-11-17): this is to be fixed when the data will be available
        # The execution_date is not the right one, we should use the CURRENT_DATE() instead of the day before
        return f"""
        SELECT
            DISTINCT offer_id as offerId,
            nb_consult_last_30_days as numberOfViews,
        FROM
            `{settings.BIG_QUERY_NOTIFICATIONS_TABLE_BASENAME}.{TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE}`
        WHERE
            offerer_id = @offerer_id
        AND
            DATE(execution_date) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
        ORDER BY numberOfViews DESC
        LIMIT 3
        """

    model = TopOffersData


class OffererTotalViewsLast30Days(pydantic_v1.BaseModel):
    totalViews: int


class OffererTotalViewsLast30DaysQuery(BaseQuery):
    @property
    def raw_query(self) -> str:
        return f"""
        SELECT
            IFNULL(SUM(nb_daily_consult), 0) as totalViews
        FROM
            `{settings.BIG_QUERY_NOTIFICATIONS_TABLE_BASENAME}.{DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE}`
        WHERE
            offerer_id = @offerer_id
        AND
            day_seniority <= 30
        """

    model = OffererTotalViewsLast30Days
