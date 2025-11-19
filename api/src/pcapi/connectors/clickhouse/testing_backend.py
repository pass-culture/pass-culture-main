from sqlalchemy import engine

from . import queries
from . import query_mock
from .backend import BaseBackend


class TestingBackend(BaseBackend):
    def _get_engine(self) -> engine.Engine:
        raise NotImplementedError

    def run_query(self, query: str, params: dict) -> list:
        if query == queries.TotalExpectedRevenueQuery().raw_query:
            return query_mock.TOTAL_EXPECTED_REVENUE
        if query == queries.AggregatedCollectiveRevenueQuery().raw_query:
            return query_mock.MULTIPLE_YEARS_AGGREGATED_VENUE_COLLECTIVE_REVENUE
        if query == queries.AggregatedIndividualRevenueQuery().raw_query:
            return query_mock.MULTIPLE_YEARS_AGGREGATED_VENUE_INDIVIDUAL_REVENUE
        if query == queries.AggregatedTotalRevenueQuery().raw_query:
            return query_mock.MULTIPLE_YEARS_AGGREGATED_VENUE_TOTAL_REVENUE
        if query == queries.CountBookingsQuery().raw_query:
            return query_mock.COUNT_BOOKINGS
        if query == queries.CountOffersQuery().raw_query:
            return query_mock.COUNT_OFFERS
        return []
