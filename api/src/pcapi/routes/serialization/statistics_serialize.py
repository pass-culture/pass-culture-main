import pydantic as pydantic_v2

from pcapi.connectors.clickhouse.queries import CollectiveRevenue
from pcapi.connectors.clickhouse.queries import IndividualRevenue
from pcapi.connectors.clickhouse.queries import TotalRevenue
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class StatisticsQueryModel(HttpQueryParamsModel):
    venue_ids: list[int] = []

    @pydantic_v2.field_validator("venue_ids", mode="before")
    def parse_venue_ids(cls, venue_ids: str | int | list[int]) -> list[int]:
        if isinstance(venue_ids, str):
            return [int(venue_ids)]
        if isinstance(venue_ids, int):
            return [venue_ids]
        return venue_ids


class AggregatedRevenueModel(HttpBodyModel):
    revenue: CollectiveRevenue | IndividualRevenue | TotalRevenue
    expected_revenue: CollectiveRevenue | IndividualRevenue | TotalRevenue | None = None


class StatisticsModel(HttpBodyModel):
    income_by_year: dict[str, AggregatedRevenueModel | dict[None, None]]
