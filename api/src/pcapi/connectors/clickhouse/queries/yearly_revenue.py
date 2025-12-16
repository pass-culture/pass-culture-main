import dataclasses
import json

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class CollectiveRevenue(ClickHouseBaseModel):
    collective: float


class AggregatedCollectiveRevenueModel(ClickHouseBaseModel):
    year: int
    revenue: CollectiveRevenue
    expected_revenue: CollectiveRevenue


@dataclasses.dataclass
class _Row:
    year: int
    revenue: str
    expected_revenue: str | None


class AggregatedCollectiveRevenueQuery(BaseQuery[AggregatedCollectiveRevenueModel, _Row]):
    def _serialize_row(self, row: _Row) -> AggregatedCollectiveRevenueModel:
        return AggregatedCollectiveRevenueModel(
            year=row.year,
            revenue=CollectiveRevenue(**json.loads(row.revenue)),
            expected_revenue=CollectiveRevenue(**json.loads(row.expected_revenue)) if row.expected_revenue else None,
        )

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
            WHERE "venue_id" in :venue_ids
            GROUP BY year
            ORDER BY year
        """


class IndividualRevenue(ClickHouseBaseModel):
    individual: float


class AggregatedIndividualRevenueModel(ClickHouseBaseModel):
    year: int
    revenue: IndividualRevenue
    expected_revenue: IndividualRevenue


class AggregatedIndividualRevenueQuery(BaseQuery[AggregatedIndividualRevenueModel, _Row]):
    def _serialize_row(self, row: _Row) -> AggregatedIndividualRevenueModel:
        return AggregatedIndividualRevenueModel(
            year=row.year,
            revenue=IndividualRevenue(**json.loads(row.revenue)),
            expected_revenue=IndividualRevenue(**json.loads(row.expected_revenue)) if row.expected_revenue else None,
        )

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
            WHERE "venue_id" in :venue_ids
            GROUP BY year
            ORDER BY year
        """


class TotalRevenue(ClickHouseBaseModel):
    total: float
    collective: float
    individual: float


class AggregatedTotalRevenueModel(ClickHouseBaseModel):
    year: int
    revenue: TotalRevenue
    expected_revenue: TotalRevenue


class AggregatedTotalRevenueQuery(BaseQuery[AggregatedTotalRevenueModel, _Row]):
    def _serialize_row(self, row: _Row) -> AggregatedTotalRevenueModel:
        return AggregatedTotalRevenueModel(
            year=row.year,
            revenue=TotalRevenue(**json.loads(row.revenue)),
            expected_revenue=TotalRevenue(**json.loads(row.expected_revenue)) if row.expected_revenue else None,
        )

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
            WHERE "venue_id" in :venue_ids
            GROUP BY year
            ORDER BY year
        """
