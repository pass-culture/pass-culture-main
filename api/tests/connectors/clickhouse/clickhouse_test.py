from decimal import Decimal
from unittest import mock

from pcapi.connectors.clickhouse import queries as clickhouse_queries
from pcapi.core.testing import override_settings

from tests.connectors.clickhouse import fixtures


class GetYearlyAggregatedOffererRevenueTest:
    @override_settings(CLICKHOUSE_BACKEND="pcapi.connectors.clickhouse.testing_backend.TestingBackend")
    def test_get_yearly_revenue(self):
        venue_ids = [1, 2]

        with mock.patch("pcapi.connectors.clickhouse.testing_backend.TestingBackend.run_query") as mock_run_query:
            mock_run_query.return_value = fixtures.YEARLY_AGGREGATED_VENUE_REVENUE
            result = clickhouse_queries.YearlyAggregatedRevenueQuery(True, True).execute(venue_ids)

        assert result.income_by_year["2024"].revenue.total == Decimal("24.24")
        assert result.income_by_year["2024"].revenue.individual == Decimal("12.12")
        assert result.income_by_year["2024"].revenue.collective == Decimal("12.12")
        assert result.income_by_year["2024"].expected_revenue.total == Decimal("26.24")
        assert result.income_by_year["2024"].expected_revenue.individual == Decimal("13.12")
        assert result.income_by_year["2024"].expected_revenue.collective == Decimal("13.12")
