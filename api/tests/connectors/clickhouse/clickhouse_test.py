import datetime
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
        results = clickhouse_queries.TopOffersByViewsQuery().execute({"venue_id": 1})

        assert len(results) == 3

        first_offer = results[0]
        assert first_offer.id == "1"
        assert first_offer.views == 150
        assert first_offer.rank == 1

        second_offer = results[1]
        assert second_offer.id == "2"
        assert second_offer.views == 120
        assert second_offer.rank == 2

        third_offer = results[2]
        assert third_offer.id == "3"
        assert third_offer.views == 100
        assert third_offer.rank == 3


class GetOfferConsultationCountTest:
    def test_get_offer_consultation_count(self):
        results = clickhouse_queries.OfferConsultationCountQuery().execute({"venue_id": 1})

        assert len(results) == 2
        assert results[0].day == datetime.date(2026, 1, 1)
        assert results[0].views == 3456
        assert results[1].day == datetime.date(2026, 1, 2)
        assert results[1].views == 4567


class OfferCumulativeViewQueryTest:
    def test_offer_cumulative_view_query(self):
        results = clickhouse_queries.OfferCumulativeViewQuery().execute({"offer_id": 1})

        assert len(results) == 8
        assert results[0].day == datetime.date(2025, 12, 1)
        assert results[0].views == 5
        assert results[1].day == datetime.date(2026, 1, 1)
        assert results[1].views == 10
        assert results[2].day == datetime.date(2026, 2, 1)
        assert results[2].views == 30
        assert results[3].day == datetime.date(2026, 3, 1)
        assert results[3].views == 45
        assert results[4].day == datetime.date(2026, 4, 1)
        assert results[4].views == 80
        assert results[5].day == datetime.date(2026, 5, 1)
        assert results[5].views == 85
        assert results[6].day == datetime.date(2026, 6, 1)
        assert results[6].views == 105
        assert results[7].day == datetime.date(2026, 7, 1)
        assert results[7].views == 200


class OfferCumulativeViewCountsTest:
    view_counts = clickhouse_queries.OfferCumulativeViewCounts(
        [
            clickhouse_queries.OfferCumulativeViewModel(day=datetime.date(2026, 1, 1), views=10),
            clickhouse_queries.OfferCumulativeViewModel(day=datetime.date(2026, 2, 1), views=30),
            clickhouse_queries.OfferCumulativeViewModel(day=datetime.date(2026, 3, 1), views=45),
        ]
    )

    def test_count_before_any_data_returns_none(self):
        assert self.view_counts.count_at(datetime.datetime(2025, 12, 31)) is None

    def test_count_on_a_recorded_day_returns_that_day(self):
        assert self.view_counts.count_at(datetime.datetime(2026, 2, 1)) == 30

    def test_count_after_last_day_returns_last_value(self):
        assert self.view_counts.count_at(datetime.datetime(2026, 6, 1)) == 45

    def test_count_on_period_subtracts_views_before_start(self):
        # count_at(end=2026-03-01) - count_at(start - 1 day = 2026-01-31) = 45 - 10
        assert self.view_counts.count_on_period(datetime.datetime(2026, 2, 1), datetime.datetime(2026, 3, 1)) == 35

    def test_count_on_period_returns_none_when_no_data_before_start(self):
        assert self.view_counts.count_on_period(datetime.datetime(2026, 1, 1), datetime.datetime(2026, 3, 1)) is None

    def test_count_with_no_data_returns_none(self):
        empty = clickhouse_queries.OfferCumulativeViewCounts([])
        assert empty.count_at(datetime.datetime(2026, 1, 1)) is None
        assert empty.count_on_period(datetime.datetime(2026, 1, 1), datetime.datetime(2026, 3, 1)) is None
