from pcapi.routes.serialization.statistics_serialize import YearlyAggregatedRevenue


class BaseBackend:
    def get_yearly_aggregated_venue_revenue(self, venue_ids: list[int]) -> YearlyAggregatedRevenue:
        raise NotImplementedError()
