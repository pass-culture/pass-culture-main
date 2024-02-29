import datetime
import json
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
            `{settings.BIG_QUERY_TABLE_BASENAME}.{DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE}`
        WHERE
            offerer_id = @offerer_id
        AND
            DATE(event_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
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
            `{settings.BIG_QUERY_TABLE_BASENAME}.{TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE}`
        WHERE
            offerer_id = @offerer_id
        AND
            DATE(execution_date) > DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        QUALIFY RANK() OVER(PARTITION BY offerer_id ORDER BY execution_date DESC) = 1
        ORDER BY numberOfViews DESC
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
            `{settings.BIG_QUERY_TABLE_BASENAME}.{DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE}`
        WHERE
            offerer_id = @offerer_id
        AND
            day_seniority <= 30
        """

    model = OffererTotalViewsLast30Days


class OffererTotalViewsLast180Days(pydantic_v1.BaseModel):
    offererId: int
    dailyViews: list[OffererViewsModel]

    @pydantic_v1.validator("dailyViews", pre=True)
    @classmethod
    def validate_daily_views(cls, dailyViews: str) -> list[TopOffersData]:
        return json.loads(dailyViews)


class OffererDailyViewsLast180Days(BaseQuery):
    @property
    def raw_query(self) -> str:
        return f"""
        SELECT 
            offerer_id as offererId,
            CONCAT('[',STRING_AGG(CONCAT('{{"eventDate":"',event_date, '","numberOfViews":', IFNULL(cum_consult, 0), '}}') order by event_date), ']') AS dailyViews 
        FROM `{settings.BIG_QUERY_TABLE_BASENAME}.{DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE}`
        WHERE
            DATE(event_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
        GROUP BY offerer_id
        ORDER BY offererId
        """

    model = OffererTotalViewsLast180Days


class OffererTopOffersAndTotalViews(pydantic_v1.BaseModel):
    offererId: int
    topOffers: list[TopOffersData]
    totalViews: int | None

    @pydantic_v1.validator("topOffers", pre=True)
    @classmethod
    def validate_top_offers(cls, top_offers: str) -> list[TopOffersData]:
        return json.loads(top_offers)


class OffererTopOffersAndTotalViewsLast30Days(BaseQuery):
    @property
    def raw_query(self) -> str:
        return f"""
        WITH top_offers as (
        SELECT
            DISTINCT offerer_id,
            offer_id,
            nb_consult_last_30_days
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.{TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE}`
        WHERE
            DATE(execution_date) = (
                SELECT
                    MAX(DATE(execution_date))
                FROM
                    `{settings.BIG_QUERY_TABLE_BASENAME}.{TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE}`
                )
        ),
        total_views as (
        SELECT
            offerer_id,
            IFNULL(SUM(nb_daily_consult), 0) as totalViews
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.{DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE}`
        WHERE
            day_seniority <= 30 group by offerer_id
        )

        SELECT
            f.offerer_id as offererId,
            CONCAT('[', STRING_AGG(CONCAT('{{"offerId":', f.offer_id, ',"numberOfViews":', f.nb_consult_last_30_days,'}}' )
            ORDER BY f.nb_consult_last_30_days DESC),']') as topOffers,
            IFNULL(ta.totalViews, 0) as totalViews
        FROM
            top_offers f
        LEFT JOIN
            total_views ta
        ON f.offerer_id = ta.offerer_id
        GROUP BY f.offerer_id, ta.totalViews
        ORDER BY offererId
        """

    model = OffererTopOffersAndTotalViews
