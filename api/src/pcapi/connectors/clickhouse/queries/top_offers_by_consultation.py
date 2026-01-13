import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class TopOfferConsultationModel(ClickHouseBaseModel):
    offer_id: str
    total_views_last_30_days: int
    rank: int


@dataclasses.dataclass
class _Row:
    offer_id: str
    total_views_last_30_days: int
    rank: int


class TopOffersByConsultationQuery(BaseQuery[TopOfferConsultationModel, _Row]):
    @property
    def model(self) -> type[TopOfferConsultationModel]:
        return TopOfferConsultationModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT offer_id, consultation_cnt as total_views_last_30_days, rank
        FROM analytics.last_30_day_venue_top_offer_consultation
        WHERE venue_id = :venue_id
        ORDER BY rank ASC
        LIMIT 3;
        """
