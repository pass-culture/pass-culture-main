from datetime import date
from decimal import Decimal
from unittest import mock

from dateutil import relativedelta
import pytest

from pcapi.connectors.clickhouse_backends.clickhouse import ClickhouseBackend


@pytest.mark.usefixtures("db_session")
class GetYearlyAggregatedOffererRevenueTest:
    @mock.patch("pcapi.connectors.clickhouse_backends.clickhouse.create_engine")
    def test_get_yearly_revenue(self, create_engine):
        # FIXME: ogeber 16.10.2024 : once the sandbox has appropriate value, use factories
        # to generate Offerer & Venues and fix data
        create_engine().execute().fetchall.return_value = [
            {
                "year": date(2024, 10, 22),
                "individual_revenue": 12.123,
                "collective_revenue": 12.123,
                "total_revenue": 24.246,
                "individual_expected_revenue": 13.123,
                "collective_expected_revenue": 13.123,
                "total_expected_revenue": 26.246,
            }
        ]
        result = ClickhouseBackend().get_yearly_aggregated_venue_revenue([1])
        assert result.year["2024"].revenue.total == Decimal("24.25")
        assert result.year["2024"].revenue.individual == Decimal("12.12")
        assert result.year["2024"].revenue.collective == Decimal("12.12")
        assert result.year["2024"].expected_revenue.total == Decimal("26.25")
        assert result.year["2024"].expected_revenue.individual == Decimal("13.12")
        assert result.year["2024"].expected_revenue.collective == Decimal("13.12")

    @mock.patch("pcapi.connectors.clickhouse_backends.clickhouse.create_engine")
    def test_get_yearly_revenue_no_results(self, create_engine):
        # FIXME: ogeber 16.10.2024 : once the sandbox has appropriate value, use factories
        # to generate Offerer & Venues and fix data
        create_engine().execute().fetchall.return_value = []
        result = ClickhouseBackend().get_yearly_aggregated_venue_revenue([1])
        assert result.year == {}

    @mock.patch("pcapi.connectors.clickhouse_backends.clickhouse.create_engine")
    def test_get_yearly_revenue_several_not_continuous_years(self, create_engine):
        # FIXME: ogeber 16.10.2024 : once the sandbox has appropriate value, use factories
        # to generate Offerer & Venues and fix data
        create_engine().execute().fetchall.return_value = [
            {
                "year": date(2024, 10, 22),
                "individual_revenue": 12.123,
                "collective_revenue": 12.123,
                "total_revenue": 24.246,
                "individual_expected_revenue": 13.123,
                "collective_expected_revenue": 13.123,
                "total_expected_revenue": 26.246,
            },
            {
                "year": date(2022, 10, 22),
                "individual_revenue": 10,
                "collective_revenue": 10,
                "total_revenue": 20,
                "individual_expected_revenue": 10,
                "collective_expected_revenue": 10,
                "total_expected_revenue": 20,
            },
        ]
        result = ClickhouseBackend().get_yearly_aggregated_venue_revenue([1])
        assert result.year["2024"].revenue.total == Decimal("24.25")
        assert result.year["2024"].revenue.individual == Decimal("12.12")
        assert result.year["2024"].revenue.collective == Decimal("12.12")
        assert result.year["2024"].expected_revenue.total == Decimal("26.25")
        assert result.year["2024"].expected_revenue.individual == Decimal("13.12")
        assert result.year["2024"].expected_revenue.collective == Decimal("13.12")

        assert result.year["2023"] is None

        assert result.year["2022"].revenue.total == Decimal("20.00")
        assert result.year["2022"].revenue.individual == Decimal("10.00")
        assert result.year["2022"].revenue.collective == Decimal("10.00")
        assert result.year["2022"].expected_revenue is None
