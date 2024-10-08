from decimal import Decimal

from pcapi.routes.serialization.statistics_serialize import AggregatedRevenue
from pcapi.routes.serialization.statistics_serialize import Revenue
from pcapi.routes.serialization.statistics_serialize import YearlyAggregatedRevenue

from .base import BaseBackend


class TestBackend(BaseBackend):
    def get_yearly_aggregated_venue_revenue(self, venue_ids: list[int]) -> YearlyAggregatedRevenue:
        revenue_2024 = Revenue(
            **{
                "individual": Decimal("100.00"),
                "collective": Decimal("100.00"),
                "total": Decimal("200.00"),
            }
        )
        expected_revenue_2024 = Revenue(
            **{
                "individual": Decimal("250.00"),
                "collective": Decimal("250.00"),
                "total": Decimal("500.00"),
            }
        )
        aggregated_revenue_2024 = AggregatedRevenue(
            **{"revenue": revenue_2024, "expectedRevenue": expected_revenue_2024}
        )
        results = {"year": {"2024": aggregated_revenue_2024}}
        if venue_ids == [1002]:
            revenue_2023 = Revenue(
                **{
                    "individual": Decimal("200.00"),
                    "collective": Decimal("200.00"),
                    "total": Decimal("400.00"),
                }
            )
            aggregated_revenue_2024 = AggregatedRevenue(revenue=revenue_2023, expected_revenue=None)
            results["year"].update({"2023": aggregated_revenue_2024})
        return YearlyAggregatedRevenue(**results)
