import json
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
    total_views_6_months: int

    def __init__(self, total_views_6_months: int = 0):
        self.total_views_6_months = total_views_6_months


OFFER_CONSULTATION_COUNT = [
    MockOfferConsultationCountQueryResult(total_views_6_months=3456),
]


class MockTopOffersByConsultationQueryResult:
    offer_id: str
    total_views_last_30_days: int
    rank: int

    def __init__(self, offer_id: str, total_views_last_30_days: int, rank: int):
        self.offer_id = offer_id
        self.total_views_last_30_days = total_views_last_30_days
        self.rank = rank


TOP_OFFERS_BY_CONSULTATION = [
    MockTopOffersByConsultationQueryResult(offer_id="offer_1", total_views_last_30_days=150, rank=1),
    MockTopOffersByConsultationQueryResult(offer_id="offer_2", total_views_last_30_days=120, rank=2),
    MockTopOffersByConsultationQueryResult(offer_id="offer_3", total_views_last_30_days=100, rank=3),
]
