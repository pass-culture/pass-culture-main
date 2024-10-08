from decimal import Decimal
import json


class MockYearlyAggregatedRevenueQueryResult:
    year: int
    revenue: dict
    expected_revenue: dict

    def __init__(
        self,
        year: int = 2024,
        individual: Decimal = Decimal("12.12"),
        collective: Decimal = Decimal("12.12"),
        expected_individual: Decimal = Decimal("13.12"),
        expected_collective: Decimal = Decimal("13.12"),
    ) -> object:
        self.year = year
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
