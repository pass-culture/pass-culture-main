import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class OfferConsultationCountModel(ClickHouseBaseModel):
    total_views_6_months: int


@dataclasses.dataclass
class _Row:
    total_views_6_months: int


class OfferConsultationCountQuery(BaseQuery[OfferConsultationCountModel, _Row]):
    @property
    def model(self) -> type[OfferConsultationCountModel]:
        return OfferConsultationCountModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT sum(consultation_cnt) as total_views_6_months
        FROM analytics.daily_aggregated_venue_offer_consultation
        WHERE venue_id = :venue_id AND event_date >= today() - INTERVAL 6 MONTH;
        """
