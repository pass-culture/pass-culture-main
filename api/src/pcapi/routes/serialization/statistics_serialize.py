import typing

from pcapi.connectors.clickhouse.queries import CollectiveRevenue
from pcapi.connectors.clickhouse.queries import IndividualRevenue
from pcapi.connectors.clickhouse.queries import TotalRevenue
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.serialization.utils import ArgsAsListBeforeValidator


class StatisticsQueryModel(HttpQueryParamsModel):
    venue_ids: typing.Annotated[list[int], ArgsAsListBeforeValidator] = []


class AggregatedRevenueModel(HttpBodyModel):
    revenue: CollectiveRevenue | IndividualRevenue | TotalRevenue
    expected_revenue: CollectiveRevenue | IndividualRevenue | TotalRevenue | None = None


class StatisticsModel(HttpBodyModel):
    income_by_year: dict[str, AggregatedRevenueModel | dict[None, None]]
