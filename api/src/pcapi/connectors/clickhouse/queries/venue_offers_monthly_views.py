import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class VenueOffersMonthlyViewsModel(ClickHouseBaseModel):
    total: int


@dataclasses.dataclass
class _Row:
    total: int


class VenueOffersMonthlyViewsQuery(BaseQuery[VenueOffersMonthlyViewsModel, _Row]):
    @property
    def model(self) -> type[VenueOffersMonthlyViewsModel]:
        return VenueOffersMonthlyViewsModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT sum(consultation_cnt) as total
        FROM analytics.daily_aggregated_venue_offer_consultation
        WHERE venue_id = :venue_id AND event_date >= today() - INTERVAL 30 DAY;
        """
