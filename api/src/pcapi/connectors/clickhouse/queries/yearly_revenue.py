from decimal import Decimal
import json

import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.routes.serialization.offers_serialize import to_camel


class Revenue(pydantic_v1.BaseModel):
    total: Decimal
    individual: Decimal
    collective: Decimal

    class Config:
        extra = "forbid"


class AggregatedRevenue(pydantic_v1.BaseModel):
    revenue: Revenue
    expected_revenue: Revenue

    class Config:
        extra = "forbid"
        alias_generator = to_camel


class YearlyAggregatedRevenueModel(pydantic_v1.BaseModel):
    income_by_year: dict[str, AggregatedRevenue | dict]

    class Config:
        extra = "forbid"
        alias_generator = to_camel


class YearlyAggregatedRevenueQuery(BaseQuery[YearlyAggregatedRevenueModel]):
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
    def raw_query(self) -> str:
        return """
            SELECT
                EXTRACT(YEAR FROM creation_year) AS year,
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

    @property
    def model(self) -> type[YearlyAggregatedRevenueModel]:
        return YearlyAggregatedRevenueModel
