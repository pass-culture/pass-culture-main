import json
from decimal import Decimal


class MockAggregatedRevenueQueryResult:
    year: int
    revenue: str
    expected_revenue: str

    def __init__(
        self,
        year: int = 2024,
        individual: Decimal = Decimal("12.12"),
        collective: Decimal = Decimal("12.12"),
        expected_individual: Decimal = Decimal("13.12"),
        expected_collective: Decimal = Decimal("13.12"),
        only_collective: bool = False,
        only_individual: bool = False,
    ):
        self.year = year
        if only_collective:
            self.revenue = json.dumps({"collective": str(collective)})
            self.expected_revenue = json.dumps({"collective": str(expected_collective)})
        elif only_individual:
            self.revenue = json.dumps({"individual": str(individual)})
            self.expected_revenue = json.dumps({"individual": str(expected_individual)})
        else:
            self.revenue = json.dumps(
                {"individual": str(individual), "collective": str(collective), "total": str(individual + collective)}
            )
            self.expected_revenue = json.dumps(
                {
                    "individual": str(expected_individual),
                    "collective": str(expected_collective),
                    "total": str(expected_individual + expected_collective),
                }
            )


AGGREGATED_TOTAL_VENUE_REVENUE = [MockAggregatedRevenueQueryResult()]
MULTIPLE_YEARS_AGGREGATED_VENUE_TOTAL_REVENUE = [
    MockAggregatedRevenueQueryResult(),
    MockAggregatedRevenueQueryResult(2022, Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), Decimal("22.12")),
]
MULTIPLE_YEARS_AGGREGATED_VENUE_COLLECTIVE_REVENUE = [
    MockAggregatedRevenueQueryResult(only_collective=True),
    MockAggregatedRevenueQueryResult(
        2022, Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), only_collective=True
    ),
]
MULTIPLE_YEARS_AGGREGATED_VENUE_INDIVIDUAL_REVENUE = [
    MockAggregatedRevenueQueryResult(only_individual=True),
    MockAggregatedRevenueQueryResult(
        2022, Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), only_individual=True
    ),
]
