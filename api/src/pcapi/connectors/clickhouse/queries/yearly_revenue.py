from decimal import Decimal
import json

import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.routes.serialization.offers_serialize import to_camel


class IndividualRevenue(pydantic_v1.BaseModel):
    individual: Decimal

    class Config:
        extra = "forbid"


class CollectiveRevenue(pydantic_v1.BaseModel):
    collective: Decimal

    class Config:
        extra = "forbid"


class CollectiveAndIndividualRevenue(IndividualRevenue, CollectiveRevenue):
    total: Decimal

    class Config:
        extra = "forbid"


class AggregatedRevenue(pydantic_v1.BaseModel):
    revenue: CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue
    expected_revenue: CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue | None

    class Config:
        extra = "forbid"
        alias_generator = to_camel


class YearlyAggregatedRevenueModel(pydantic_v1.BaseModel):
    income_by_year: dict[str, AggregatedRevenue | dict[None, None]]

    class Config:
        extra = "forbid"
        alias_generator = to_camel


class YearlyAggregatedRevenueQueryMixin:
    def _format_result(self, results: list) -> dict:
        return {
            "incomeByYear": {
                result.year: {
                    "revenue": json.loads(result.revenue),
                    "expectedRevenue": json.loads(result.expected_revenue),
                }
                for result in results
            }
        }

    @property
    def model(self) -> type[YearlyAggregatedRevenueModel]:
        return YearlyAggregatedRevenueModel


class YearlyAggregatedCollectiveRevenueQuery(
    YearlyAggregatedRevenueQueryMixin, BaseQuery[YearlyAggregatedRevenueModel]
):
    @property
    def raw_query(self) -> str:
        return """
            SELECT
                EXTRACT(YEAR FROM year) AS year,
                toJSONString(map(
                    'collective', ROUND(SUM(revenue),2))
                ) as revenue,
                toJSONString(map(
                    'collective', ROUND(SUM(expected_revenue),2))
                ) as expected_revenue
            FROM analytics.yearly_aggregated_venue_collective_revenue
            WHERE "venue_id" in %s
            GROUP BY year
            ORDER BY year
        """


class YearlyAggregatedIndividualRevenueQuery(
    YearlyAggregatedRevenueQueryMixin, BaseQuery[YearlyAggregatedRevenueModel]
):
    @property
    def raw_query(self) -> str:
        return """
            SELECT
                EXTRACT(YEAR FROM year) AS year,
                toJSONString(map(
                    'individual', ROUND(SUM(revenue),2))
                ) as revenue,
                toJSONString(map(
                    'individual', ROUND(SUM(expected_revenue),2))
                ) as expected_revenue
            FROM analytics.yearly_aggregated_venue_individual_revenue
            WHERE "venue_id" in %s
            GROUP BY year
            ORDER BY year
        """


class YearlyAggregatedRevenueQuery(YearlyAggregatedRevenueQueryMixin, BaseQuery[YearlyAggregatedRevenueModel]):
    @property
    def raw_query(self) -> str:
        return """
            SELECT
                EXTRACT(YEAR FROM year) AS year,
                toJSONString(map(
                    'individual', ROUND(SUM(individual_revenue),2),
                    'collective', ROUND(SUM(collective_revenue),2),
                    'total', ROUND(SUM(total_revenue),2))
                ) as revenue,
                toJSONString(map(
                    'individual', ROUND(SUM(individual_expected_revenue),2),
                    'collective', ROUND(SUM(collective_expected_revenue),2),
                    'total', ROUND(SUM(total_expected_revenue),2))
                ) as expected_revenue
            FROM analytics.yearly_aggregated_venue_revenue
            WHERE "venue_id" in %s
            GROUP BY year
            ORDER BY year
        """
