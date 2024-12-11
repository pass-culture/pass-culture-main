from decimal import Decimal
import json


class MockYearlyAggregatedRevenueQueryResult:
    year: int
    revenue: str
    expected_revenue: str

    def __init__(  # pylint: disable=too-many-positional-arguments
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


YEARLY_AGGREGATED_VENUE_REVENUE = [MockYearlyAggregatedRevenueQueryResult()]
YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS = [
    MockYearlyAggregatedRevenueQueryResult(),
    MockYearlyAggregatedRevenueQueryResult(
        2022, Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), Decimal("22.12")
    ),
]
YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS_ONLY_COLLECTIVE = [
    MockYearlyAggregatedRevenueQueryResult(only_collective=True),
    MockYearlyAggregatedRevenueQueryResult(
        2022, Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), only_collective=True
    ),
]
YEARLY_AGGREGATED_VENUE_REVENUE_MULTIPLE_YEARS_ONLY_INDIVIDUAL = [
    MockYearlyAggregatedRevenueQueryResult(only_individual=True),
    MockYearlyAggregatedRevenueQueryResult(
        2022, Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), Decimal("22.12"), only_individual=True
    ),
]
