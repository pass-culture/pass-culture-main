import json
from decimal import Decimal
from typing import Any

import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery


class CollectiveRevenue(pydantic_v1.BaseModel):
    collective: Decimal

    class Config:
        extra = "forbid"


class CollectiveRevenueGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        row = self._obj
        if key == "revenue":
            return CollectiveRevenue(**json.loads(row.revenue))

        if key == "expected_revenue":
            if row.expected_revenue is None:
                return None
            return CollectiveRevenue(**json.loads(row.expected_revenue))

        return super().get(key, default)


class AggregatedCollectiveRevenueModel(pydantic_v1.BaseModel):
    year: int
    revenue: CollectiveRevenue
    expected_revenue: CollectiveRevenue

    class Config:
        extra = "forbid"
        orm_mode = True
        getter_dict = CollectiveRevenueGetterDict


class AggregatedCollectiveRevenueQuery(BaseQuery[AggregatedCollectiveRevenueModel]):
    @property
    def model(self) -> type[AggregatedCollectiveRevenueModel]:
        return AggregatedCollectiveRevenueModel

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                EXTRACT(YEAR FROM year) AS year,
                toJSONString(map(
                    'collective', ROUND(SUM(revenue), 2))
                ) as revenue,
                toJSONString(map(
                    'collective', ROUND(SUM(expected_revenue), 2))
                ) as expected_revenue
            FROM analytics.yearly_aggregated_venue_collective_revenue
            WHERE "venue_id" in %s
            GROUP BY year
            ORDER BY year
        """


class IndividualRevenue(pydantic_v1.BaseModel):
    individual: Decimal

    class Config:
        extra = "forbid"


class IndividualRevenueGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        row = self._obj
        if key == "revenue":
            return IndividualRevenue(**json.loads(row.revenue))

        if key == "expected_revenue":
            if row.expected_revenue is None:
                return None
            return IndividualRevenue(**json.loads(row.expected_revenue))

        return super().get(key, default)


class AggregatedIndividualRevenueModel(pydantic_v1.BaseModel):
    year: int
    revenue: IndividualRevenue
    expected_revenue: IndividualRevenue

    class Config:
        extra = "forbid"
        orm_mode = True
        getter_dict = IndividualRevenueGetterDict


class AggregatedIndividualRevenueQuery(BaseQuery[AggregatedIndividualRevenueModel]):
    @property
    def model(self) -> type[AggregatedIndividualRevenueModel]:
        return AggregatedIndividualRevenueModel

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                EXTRACT(YEAR FROM year) AS year,
                toJSONString(map(
                    'individual', ROUND(SUM(revenue), 2))
                ) as revenue,
                toJSONString(map(
                    'individual', ROUND(SUM(expected_revenue), 2))
                ) as expected_revenue
            FROM analytics.yearly_aggregated_venue_individual_revenue
            WHERE "venue_id" in %s
            GROUP BY year
            ORDER BY year
        """


class TotalRevenue(IndividualRevenue, CollectiveRevenue):
    total: Decimal

    class Config:
        extra = "forbid"


class TotalRevenueGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        row = self._obj
        if key == "revenue":
            return TotalRevenue(**json.loads(row.revenue))

        if key == "expected_revenue":
            if row.expected_revenue is None:
                return None
            return TotalRevenue(**json.loads(row.expected_revenue))

        return super().get(key, default)


class AggregatedTotalRevenueModel(pydantic_v1.BaseModel):
    year: int
    revenue: TotalRevenue
    expected_revenue: TotalRevenue

    class Config:
        extra = "forbid"
        orm_mode = True
        getter_dict = TotalRevenueGetterDict


class AggregatedTotalRevenueQuery(BaseQuery[AggregatedTotalRevenueModel]):
    @property
    def model(self) -> type[AggregatedTotalRevenueModel]:
        return AggregatedTotalRevenueModel

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                EXTRACT(YEAR FROM year) AS year,
                toJSONString(map(
                    'individual', ROUND(SUM(individual_revenue), 2),
                    'collective', ROUND(SUM(collective_revenue), 2),
                    'total', ROUND(SUM(total_revenue), 2))
                ) as revenue,
                toJSONString(map(
                    'individual', ROUND(SUM(individual_expected_revenue), 2),
                    'collective', ROUND(SUM(collective_expected_revenue), 2),
                    'total', ROUND(SUM(total_expected_revenue), 2))
                ) as expected_revenue
            FROM analytics.yearly_aggregated_venue_revenue
            WHERE "venue_id" in %s
            GROUP BY year
            ORDER BY year
        """
