import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class CountOffers(ClickHouseBaseModel):
    active_individual_offers: int
    inactive_individual_offers: int
    active_collective_offers: int
    inactive_collective_offers: int


@dataclasses.dataclass
class _Row:
    active_individual_offers: int
    inactive_individual_offers: int
    active_collective_offers: int
    inactive_collective_offers: int


class CountOffersQuery(BaseQuery[CountOffers, _Row]):
    @property
    def model(self) -> type[CountOffers]:
        return CountOffers

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                SUM(total_active_offers) AS active_individual_offers,
                SUM(total_pending_offers + total_inactive_non_rejected_offers) AS inactive_individual_offers,
                SUM(total_active_collective_offers) AS active_collective_offers,
                SUM(total_pending_collective_offers + total_inactive_non_rejected_collective_offers) AS inactive_collective_offers
            FROM intermediate.venue_offer_statistic
            WHERE "venue_id" IN :venue_ids
        """
