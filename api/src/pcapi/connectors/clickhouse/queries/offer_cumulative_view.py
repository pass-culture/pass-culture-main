import bisect
import dataclasses
import datetime

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class OfferCumulativeViewModel(ClickHouseBaseModel):
    day: datetime.date
    views: int


class OfferCumulativeViewCounts:
    def __init__(self, views_per_day: list[OfferCumulativeViewModel]) -> None:
        self._views_per_day = views_per_day
        self._sorted_days = [row.day for row in views_per_day]

    # Returns the cumulated views at a date, or None if there is no data before that date
    def count_at(self, target_date: datetime.datetime) -> int | None:
        position = bisect.bisect_right(self._sorted_days, target_date.date())
        return self._views_per_day[position - 1].views if position > 0 else None

    def count_on_period(self, start_date: datetime.datetime, end_date: datetime.datetime) -> int | None:
        views_at_end = self.count_at(end_date)
        # The cumulated value at a date includes views on that date, so the lower bound to subtract is the day before
        views_before_start = self.count_at(start_date - datetime.timedelta(days=1))

        return views_at_end - views_before_start if views_at_end and views_before_start else None


@dataclasses.dataclass
class _Row:
    day: datetime.date
    views: int


class OfferCumulativeViewQuery(BaseQuery[OfferCumulativeViewModel, _Row]):
    @property
    def model(self) -> type[OfferCumulativeViewModel]:
        return OfferCumulativeViewModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT partition_date AS day, consultation_cumulative_cnt AS views
        FROM analytics.offer_consultation_cumulative
        WHERE offer_id = :offer_id
        ORDER BY partition_date
        """
