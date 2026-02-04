import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class OfferMonthlyViewModel(ClickHouseBaseModel):
    month: int
    views: int


@dataclasses.dataclass
class _Row:
    month: int
    views: int


class OfferConsultationCountQuery(BaseQuery[OfferMonthlyViewModel, _Row]):
    model = OfferMonthlyViewModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT EXTRACT(MONTH from event_date) as month, sum(consultation_cnt) as views
        FROM analytics.daily_aggregated_venue_offer_consultation
        WHERE venue_id = :venue_id AND event_date >= today() - INTERVAL 6 MONTH
        GROUP BY month
        """
