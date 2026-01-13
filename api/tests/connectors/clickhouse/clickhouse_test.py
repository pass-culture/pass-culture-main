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
            results = clickhouse_queries.AggregatedTotalRevenueQuery().execute({"venue_ids": tuple(venue_ids)})

        (result_2024,) = [result for result in results if result.year == 2024]
        assert result_2024.revenue.total == 24.24
        assert result_2024.revenue.individual == 12.12
        assert result_2024.revenue.collective == 12.12
        assert result_2024.expected_revenue.total == 26.24
        assert result_2024.expected_revenue.individual == 13.12
        assert result_2024.expected_revenue.collective == 13.12


class GetTopOffersByConsultationTest:
    def test_get_top_offers_by_consultation(self):
        results = clickhouse_queries.TopOffersByConsultationQuery().execute({"venue_id": 1})

        assert len(results) == 3

        first_offer = results[0]
        assert first_offer.offer_id == "offer_1"
        assert first_offer.total_views_last_30_days == 150
        assert first_offer.rank == 1

        second_offer = results[1]
        assert second_offer.offer_id == "offer_2"
        assert second_offer.total_views_last_30_days == 120
        assert second_offer.rank == 2

        third_offer = results[2]
        assert third_offer.offer_id == "offer_3"
        assert third_offer.total_views_last_30_days == 100
        assert third_offer.rank == 3


class GetOfferConsultationCountTest:
    def test_get_offer_consultation_count(self):
        results = clickhouse_queries.OfferConsultationCountQuery().execute({"venue_id": 1})

        assert len(results) == 1
        assert results[0].total_views_6_months == 3456
