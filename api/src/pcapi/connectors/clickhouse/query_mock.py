import datetime
import json
from dataclasses import dataclass
from decimal import Decimal

from .queries import count_bookings
from .queries import count_offers


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
AGGREGATED_VENUE_REVENUE_WITH_NO_INCOME = [
    MockAggregatedRevenueQueryResult(
        year=2026,
        individual=Decimal("0"),
        collective=Decimal("0"),
        expected_individual=Decimal("0"),
        expected_collective=Decimal("0"),
    ),
]


def get_aggregated_revenues(
    only_collective: bool = False, only_individual: bool = False
) -> list[MockAggregatedRevenueQueryResult]:
    """Generate revenues for current year + 4 last years"""

    current_year = datetime.date.today().year
    results = [
        MockAggregatedRevenueQueryResult(
            year=current_year, only_collective=only_collective, only_individual=only_individual
        )
    ]

    for delta in range(1, 5):
        year = current_year - delta
        results.append(
            MockAggregatedRevenueQueryResult(
                year,
                Decimal("22.12"),
                Decimal("22.12"),
                Decimal("22.12"),
                Decimal("22.12"),
                only_collective=only_collective,
                only_individual=only_individual,
            )
        )

    return results


class MockTotalExpectedRevenueQueryResult:
    expected_revenue: str

    def __init__(self, expected_revenue: Decimal = Decimal("70.48")):
        self.expected_revenue = str(expected_revenue)


TOTAL_EXPECTED_REVENUE = [MockTotalExpectedRevenueQueryResult()]

COUNT_BOOKINGS = [count_bookings.CountBookings(individual_bookings=876, collective_bookings=678)]
COUNT_OFFERS = [
    count_offers.CountOffers(
        active_individual_offers=125,
        inactive_individual_offers=12,
        active_collective_offers=54,
        inactive_collective_offers=2,
    ),
]


class MockOfferConsultationCountQueryResult:
    month: int
    views: int

    def __init__(self, month: int = 1, views: int = 0):
        self.month = month
        self.views = views


OFFER_CONSULTATION_COUNT = [
    MockOfferConsultationCountQueryResult(month=1, views=3456),
]


class MockTopOffersByViewsQueryResult:
    id: str
    views: int
    rank: int

    def __init__(self, id: str, views: int, rank: int):
        self.id = id
        self.views = views
        self.rank = rank


TOP_OFFERS_BY_VIEWS = [
    MockTopOffersByViewsQueryResult(id="1", views=150, rank=1),
    MockTopOffersByViewsQueryResult(id="2", views=120, rank=2),
    MockTopOffersByViewsQueryResult(id="3", views=100, rank=3),
]


@dataclass
class MockVenueOffersMonthlyViewsQuery:
    total: int


VENUE_OFFERS_MONTHLY_VIEWS = [MockVenueOffersMonthlyViewsQuery(total=256)]
