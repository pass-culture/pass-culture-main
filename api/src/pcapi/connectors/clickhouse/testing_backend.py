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
            return query_mock.get_aggregated_revenues(only_collective=True)

        if query == queries.AggregatedIndividualRevenueQuery().raw_query:
            return query_mock.get_aggregated_revenues(only_individual=True)

        if query == queries.AggregatedTotalRevenueQuery().raw_query:
            return query_mock.get_aggregated_revenues()

        if query == queries.CountBookingsQuery().raw_query:
            return query_mock.COUNT_BOOKINGS

        if query == queries.CountOffersQuery().raw_query:
            return query_mock.COUNT_OFFERS

        if query == queries.OfferConsultationCountQuery().raw_query:
            return query_mock.OFFER_CONSULTATION_COUNT

        if query == queries.TopOffersByViewsQuery().raw_query:
            return query_mock.TOP_OFFERS_BY_VIEWS

        if query == queries.VenueOffersMonthlyViewsQuery().raw_query:
            return query_mock.VENUE_OFFERS_MONTHLY_VIEWS

        return []
