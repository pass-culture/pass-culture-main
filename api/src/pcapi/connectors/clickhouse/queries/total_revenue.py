import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class TotalExpectedRevenueModel(ClickHouseBaseModel):
    expected_revenue: float


@dataclasses.dataclass
class _Row:
    expected_revenue: float


class TotalExpectedRevenueQuery(BaseQuery[TotalExpectedRevenueModel, _Row]):
    @property
    def model(self) -> type[TotalExpectedRevenueModel]:
        return TotalExpectedRevenueModel

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                ROUND(SUM(total_expected_revenue),2) as expected_revenue
            FROM analytics.yearly_aggregated_venue_revenue
            WHERE "venue_id" in :venue_ids
        """
