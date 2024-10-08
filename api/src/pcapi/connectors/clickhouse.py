from pcapi.connectors.clickhouse_backends import clickhouse_backend
from pcapi.connectors.clickhouse_backends.base import YearlyAggregatedRevenue


def get_yearly_aggregated_revenue(venue_ids: list[int]) -> YearlyAggregatedRevenue:
    return clickhouse_backend.get_yearly_aggregated_venue_revenue(venue_ids)
