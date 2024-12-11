from decimal import Decimal
from unittest import mock

import pytest

from pcapi.connectors.clickhouse import queries as clickhouse_queries
from pcapi.connectors.clickhouse import query_mock


class GetYearlyAggregatedOffererRevenueTest:
    @pytest.mark.settings(CLICKHOUSE_BACKEND="pcapi.connectors.clickhouse.testing_backend.TestingBackend")
    def test_get_yearly_revenue(self):
        venue_ids = [1, 2]

        with mock.patch("pcapi.connectors.clickhouse.testing_backend.TestingBackend.run_query") as mock_run_query:
            mock_run_query.return_value = query_mock.AGGREGATED_TOTAL_VENUE_REVENUE
            results = clickhouse_queries.AggregatedTotalRevenueQuery().execute(venue_ids)

        (result_2024,) = [result for result in results if result.year == 2024]
        assert result_2024.revenue.total == Decimal("24.24")
        assert result_2024.revenue.individual == Decimal("12.12")
        assert result_2024.revenue.collective == Decimal("12.12")
        assert result_2024.expected_revenue.total == Decimal("26.24")
        assert result_2024.expected_revenue.individual == Decimal("13.12")
        assert result_2024.expected_revenue.collective == Decimal("13.12")
