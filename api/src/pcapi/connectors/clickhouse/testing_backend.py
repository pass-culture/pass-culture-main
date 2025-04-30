import typing

from sqlalchemy import engine

from .backend import BaseBackend
from .queries import AggregatedCollectiveRevenueQuery
from .queries import AggregatedIndividualRevenueQuery
from .queries import AggregatedTotalRevenueQuery
from .queries import TotalExpectedRevenueQuery
from .query_mock import MULTIPLE_YEARS_AGGREGATED_VENUE_COLLECTIVE_REVENUE
from .query_mock import MULTIPLE_YEARS_AGGREGATED_VENUE_INDIVIDUAL_REVENUE
from .query_mock import MULTIPLE_YEARS_AGGREGATED_VENUE_TOTAL_REVENUE


class TestingBackend(BaseBackend):
    def _get_engine(self) -> engine.Engine:
        raise NotImplementedError

    def run_query(self, query: str, params: typing.Tuple) -> list:
        if query == TotalExpectedRevenueQuery().raw_query:
            return []
        if query == AggregatedCollectiveRevenueQuery().raw_query:
            return MULTIPLE_YEARS_AGGREGATED_VENUE_COLLECTIVE_REVENUE
        if query == AggregatedIndividualRevenueQuery().raw_query:
            return MULTIPLE_YEARS_AGGREGATED_VENUE_INDIVIDUAL_REVENUE
        if query == AggregatedTotalRevenueQuery().raw_query:
            return MULTIPLE_YEARS_AGGREGATED_VENUE_TOTAL_REVENUE
        return []
