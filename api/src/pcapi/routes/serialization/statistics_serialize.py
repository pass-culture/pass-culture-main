import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries import CollectiveRevenue
from pcapi.connectors.clickhouse.queries import IndividualRevenue
from pcapi.connectors.clickhouse.queries import TotalRevenue
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel


class StatisticsQueryModel(BaseModel):
    venue_ids: list[int] = []

    @pydantic_v1.validator("venue_ids", pre=True)
    def parse_venue_ids(cls, venue_ids: str | int | list[int]) -> list[int]:
        if isinstance(venue_ids, str):
            return [int(venue_ids)]
        if isinstance(venue_ids, int):
            return [venue_ids]
        return venue_ids


class AggregatedRevenueModel(ConfiguredBaseModel):
    revenue: CollectiveRevenue | IndividualRevenue | TotalRevenue
    expected_revenue: CollectiveRevenue | IndividualRevenue | TotalRevenue | None


class StatisticsModel(ConfiguredBaseModel):
    income_by_year: dict[str, AggregatedRevenueModel | dict[None, None]]

    class Config:
        extra = "forbid"
