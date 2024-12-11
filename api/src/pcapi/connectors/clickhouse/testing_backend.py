import typing

from sqlalchemy import engine

from .backend import BaseBackend
from .queries import TotalAggregatedRevenueQuery
from .queries import YearlyAggregatedCollectiveRevenueQuery
from .queries import YearlyAggregatedIndividualRevenueQuery
from .queries import YearlyAggregatedRevenueQuery
from .query_mock import YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS
from .query_mock import YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS_ONLY_COLLECTIVE
from .query_mock import YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS_ONLY_INDIVIDUAL


class TestingBackend(BaseBackend):

    def _get_engine(self) -> engine.Engine:
        raise NotImplementedError

    def run_query(self, query: str, params: typing.Tuple) -> list:
        if query == TotalAggregatedRevenueQuery().raw_query:
            return []
        if query == YearlyAggregatedCollectiveRevenueQuery().raw_query:
            return YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS_ONLY_COLLECTIVE
        if query == YearlyAggregatedIndividualRevenueQuery().raw_query:
            return YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS_ONLY_INDIVIDUAL
        if query == YearlyAggregatedRevenueQuery().raw_query:
            return YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS
        return []
