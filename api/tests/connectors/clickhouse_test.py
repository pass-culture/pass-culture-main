from decimal import Decimal
from unittest import mock

import pydantic.v1 as pydantic_v1
import pytest

from pcapi.connectors import clickhouse
from pcapi.connectors.clickhouse_backends.base import YearlyAggregatedRevenue
from pcapi.connectors.clickhouse_backends.clickhouse import ClickhouseBackend
from pcapi.connectors.clickhouse_backends.test import TestBackend
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class GetYearlyAggregatedOffererRevenueTest:
    # @mock.patch("pcapi.core.external.clickhouse.clickhouse_backend", TestBackend())
    # def test_get_yearly_revenue_mock(self):
    #     offerer = offerers_factories.OffererFactory(name="Gestionnaire de plein de musées")
    #     result = clickhouse.get_yearly_aggregated_revenue(offerer.id)
    #     breakpoint()
    #     assert result["2024"].revenue == 60219.0
    #     assert result["2024"].expected_revenue == 60229.0

    @mock.patch("pcapi.core.external.clickhouse.clickhouse_backend", ClickhouseBackend())
    def test_get_yearly_revenue(self):
        offerer = offerers_factories.OffererFactory(name="Gestionnaire de plein de musées")
        # FIXME: ogeber 16.10.2024 : once the sandbox has appropriate value, use factories
        # to generate Offerer & Venues and fix data
        venue_ids = [1000]
        result = clickhouse.get_yearly_aggregated_revenue(venue_ids)
        assert result.year["2024"].revenue.total == Decimal("10.1")
        assert result.year["2024"].revenue.individual == Decimal("10.1")
        assert result.year["2024"].revenue.collective == Decimal("0.0")

    @mock.patch("pcapi.core.external.clickhouse.clickhouse_backend", ClickhouseBackend())
    def test_get_yearly_revenue_several_venues(self):
        offerer = offerers_factories.OffererFactory(name="Gestionnaire de plein de musées")
        # FIXME: ogeber 16.10.2024 : once the sandbox has appropriate value, use factories
        # to generate Offerer & Venues and fix data
        venue_ids = [1000, 1001]
        result = clickhouse.get_yearly_aggregated_revenue(venue_ids)
        assert result.year["2024"].revenue.total == Decimal("20.2")
        assert result.year["2024"].revenue.individual == Decimal("20.2")
        assert result.year["2024"].revenue.collective == Decimal("0.0")


# TODO : Add tests over several years
