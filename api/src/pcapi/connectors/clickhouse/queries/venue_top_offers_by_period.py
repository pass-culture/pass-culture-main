import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class VenueTopOfferByPeriodModel(ClickHouseBaseModel):
    offer_id: str
    consultation_cnt_3m: int | None
    consultation_cnt_6m: int | None
    rank_3m: int | None
    rank_6m: int | None


@dataclasses.dataclass
class _Row:
    offer_id: str
    consultation_cnt_3m: int | None
    consultation_cnt_6m: int | None
    rank_3m: int | None
    rank_6m: int | None


class VenueTopOffersByPeriodQuery(BaseQuery[VenueTopOfferByPeriodModel, _Row]):
    @property
    def model(self) -> type[VenueTopOfferByPeriodModel]:
        return VenueTopOfferByPeriodModel

    @property
    def raw_query(self) -> str:
        # TODO(@tpommellet): table name to be confirmed by the data team
        return """
        SELECT offer_id, consultation_cnt_3m, consultation_cnt_6m, rank_3m, rank_6m
        FROM analytics.venue_top_offer_consultation_3m_6m
        WHERE venue_id = :venue_id;
        """
