import dataclasses
import datetime

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class VenueOffersViewsByMonthModel(ClickHouseBaseModel):
    month: datetime.date
    views: int


@dataclasses.dataclass
class _Row:
    month: datetime.date
    views: int


class VenueOffersViewsByMonthQuery(BaseQuery[VenueOffersViewsByMonthModel, _Row]):
    @property
    def model(self) -> type[VenueOffersViewsByMonthModel]:
        return VenueOffersViewsByMonthModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT toStartOfMonth(event_date) as month, sum(consultation_cnt) as views
        FROM analytics.daily_aggregated_venue_offer_consultation
        WHERE venue_id = :venue_id AND event_date >= subtractMonths(toStartOfMonth(today()), 5)
        GROUP BY month
        ORDER BY month ASC;
        """
