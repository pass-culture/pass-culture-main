import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery


class CountOffers(pydantic_v1.BaseModel):
    active_individual_offers: int
    inactive_individual_offers: int
    active_collective_offers: int
    inactive_collective_offers: int

    class Config:
        extra = "forbid"
        orm_mode = True


class CountOffersQuery(BaseQuery[CountOffers]):
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
