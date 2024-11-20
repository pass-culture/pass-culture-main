from decimal import Decimal

import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.routes.serialization.offers_serialize import to_camel


class TotalAggregatedRevenueModel(pydantic_v1.BaseModel):
    expected_revenue: Decimal

    class Config:
        extra = "forbid"
        alias_generator = to_camel


class TotalAggregatedRevenueQuery(BaseQuery[TotalAggregatedRevenueModel]):
    def _format_result(self, rows: list) -> dict:
        return {"expectedRevenue": rows[0].expected_revenue}

    @property
    def model(self) -> type[TotalAggregatedRevenueModel]:
        return TotalAggregatedRevenueModel

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                ROUND(SUM(total_expected_revenue),2) as expected_revenue
            FROM analytics.yearly_aggregated_venue_revenue
            WHERE "venue_id" in %s
        """
