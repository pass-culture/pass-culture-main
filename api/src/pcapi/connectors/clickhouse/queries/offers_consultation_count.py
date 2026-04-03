import dataclasses
import datetime

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class OfferDailyViewModel(ClickHouseBaseModel):
    day: datetime.date
    views: int


@dataclasses.dataclass
class _Row:
    day: datetime.date
    views: int


class OfferConsultationCountQuery(BaseQuery[OfferDailyViewModel, _Row]):
    model = OfferDailyViewModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT event_date as day, consultation_cnt as views
        FROM analytics.daily_aggregated_venue_offer_consultation
        WHERE venue_id = :venue_id AND event_date >= today() - INTERVAL 6 MONTH
        """
