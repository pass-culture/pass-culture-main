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
        individual=Decimal(0),
        collective=Decimal(0),
        expected_individual=Decimal(0),
        expected_collective=Decimal(0),
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
    day: datetime.date
    views: int

    def __init__(self, day: datetime.date, views: int = 0):
        self.day = day
        self.views = views


OFFER_CONSULTATION_COUNT = [
    MockOfferConsultationCountQueryResult(day=datetime.date(2026, 1, 1), views=3456),
    MockOfferConsultationCountQueryResult(day=datetime.date(2026, 1, 2), views=4567),
]


class MockOfferCumulativeViewQueryResult:
    day: datetime.date
    views: int

    def __init__(self, day: datetime.date, views: int = 0):
        self.day = day
        self.views = views


OFFER_CONSULTATION_CUMULATIVE_COUNT = [
    MockOfferCumulativeViewQueryResult(day=datetime.date(2025, 12, 1), views=5),
    MockOfferCumulativeViewQueryResult(day=datetime.date(2026, 1, 1), views=10),
    MockOfferCumulativeViewQueryResult(day=datetime.date(2026, 2, 1), views=30),
    MockOfferCumulativeViewQueryResult(day=datetime.date(2026, 3, 1), views=45),
    MockOfferCumulativeViewQueryResult(day=datetime.date(2026, 4, 1), views=80),
    MockOfferCumulativeViewQueryResult(day=datetime.date(2026, 5, 1), views=85),
    MockOfferCumulativeViewQueryResult(day=datetime.date(2026, 6, 1), views=105),
    MockOfferCumulativeViewQueryResult(day=datetime.date(2026, 7, 1), views=200),
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


@dataclass
class MockVenueTopOffersQueryResult:
    offer_id: str
    consultation_cnt_3m: int | None
    consultation_cnt_6m: int | None
    rank_3m: int | None
    rank_6m: int | None


VENUE_TOP_OFFERS_BY_PERIOD = [
    MockVenueTopOffersQueryResult(offer_id="1", consultation_cnt_3m=150, consultation_cnt_6m=300, rank_3m=1, rank_6m=1),
    MockVenueTopOffersQueryResult(offer_id="2", consultation_cnt_3m=120, consultation_cnt_6m=200, rank_3m=2, rank_6m=3),
    MockVenueTopOffersQueryResult(offer_id="3", consultation_cnt_3m=100, consultation_cnt_6m=250, rank_3m=3, rank_6m=2),
    MockVenueTopOffersQueryResult(
        offer_id="4", consultation_cnt_3m=None, consultation_cnt_6m=180, rank_3m=None, rank_6m=4
    ),
]


@dataclass
class MockVenueOffersConsultationsByMonthQueryResult:
    month: datetime.date
    views: int


VENUE_OFFERS_VIEWS_BY_MONTH = [
    MockVenueOffersConsultationsByMonthQueryResult(month=datetime.date(2026, 4, 1), views=10),
    MockVenueOffersConsultationsByMonthQueryResult(month=datetime.date(2026, 5, 1), views=20),
    MockVenueOffersConsultationsByMonthQueryResult(month=datetime.date(2026, 6, 1), views=30),
    MockVenueOffersConsultationsByMonthQueryResult(month=datetime.date(2026, 7, 1), views=40),
    MockVenueOffersConsultationsByMonthQueryResult(month=datetime.date(2026, 8, 1), views=50),
    MockVenueOffersConsultationsByMonthQueryResult(month=datetime.date(2026, 9, 1), views=60),
]
