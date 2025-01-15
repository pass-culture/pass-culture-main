from decimal import Decimal

import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery


class TotalExpectedRevenueModel(pydantic_v1.BaseModel):
    expected_revenue: Decimal

    class Config:
        extra = "forbid"
        orm_mode = True


class TotalExpectedRevenueQuery(BaseQuery[TotalExpectedRevenueModel]):
    @property
    def model(self) -> type[TotalExpectedRevenueModel]:
        return TotalExpectedRevenueModel

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                ROUND(SUM(total_expected_revenue),2) as expected_revenue
            FROM analytics.yearly_aggregated_venue_revenue
            WHERE "venue_id" in %s
        """
