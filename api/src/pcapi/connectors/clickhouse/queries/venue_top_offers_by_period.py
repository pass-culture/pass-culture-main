import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class VenueTopOfferByPeriodModel(ClickHouseBaseModel):
    offer_id: str
    consultation_cnt: int
    rank: int


@dataclasses.dataclass
class _Row:
    offer_id: str
    consultation_cnt: int
    rank: int


class VenueTopOffersByPeriodQuery(BaseQuery[VenueTopOfferByPeriodModel, _Row]):
    def __init__(self, months: int) -> None:
        super().__init__()
        self.months = months

    @property
    def model(self) -> type[VenueTopOfferByPeriodModel]:
        return VenueTopOfferByPeriodModel

    @property
    def raw_query(self) -> str:
        return f"""
        SELECT offer_id, consultation_cnt, rank
        FROM analytics.last_{self.months}months_venue_top_offer_consultation
        WHERE venue_id = :venue_id
        ORDER BY rank ASC;
        """
