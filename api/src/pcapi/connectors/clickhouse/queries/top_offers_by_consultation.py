import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class TopOffersByViewsModel(ClickHouseBaseModel):
    id: str
    views: int
    rank: int


@dataclasses.dataclass
class _Row:
    id: str
    views: int
    rank: int


class TopOffersByViewsQuery(BaseQuery[TopOffersByViewsModel, _Row]):
    @property
    def model(self) -> type[TopOffersByViewsModel]:
        return TopOffersByViewsModel

    @property
    def raw_query(self) -> str:
        return """
        SELECT offer_id as id, consultation_cnt as views, rank
        FROM analytics.last_30_day_venue_top_offer_consultation
        WHERE venue_id = :venue_id
        ORDER BY rank ASC
        LIMIT 3;
        """
