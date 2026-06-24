import datetime

import pytest
import time_machine

import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.highlights.factories as highlights_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.connectors.clickhouse.queries.offer_cumulative_view import OfferCumulativeViewCounts
from pcapi.connectors.clickhouse.query_mock import OFFER_CONSULTATION_CUMULATIVE_COUNT as VIEWS_PER_DAY
from pcapi.core.offers.constants import ExposureEventType
from pcapi.routes.serialization.offer_exposure_serialize import GetOfferExposureResponseModel
from pcapi.utils import db as db_utils


pytestmark = pytest.mark.usefixtures("db_session")

CUMULATIVE_VIEWS = OfferCumulativeViewCounts(VIEWS_PER_DAY)


class BuildOfferExposureTest:
    @pytest.fixture(autouse=True)
    def _freeze_today(self):
        with time_machine.travel("2026-06-01 12:00:00", tick=False):
            yield

    def test_offer_without_enhancement_events(self):
        offer = offers_factories.OfferFactory()

        response = GetOfferExposureResponseModel.build(offer, CUMULATIVE_VIEWS)

        assert response.views == 105
        assert response.events == []

    def test_headline_offer_event_with_end_date(self):
        headline = offers_factories.HeadlineOfferFactory(
            timespan=(datetime.datetime(2026, 1, 1), datetime.datetime(2026, 2, 1))
        )

        response = GetOfferExposureResponseModel.build(headline.offer, CUMULATIVE_VIEWS)

        assert len(response.events) == 1
        event = response.events[0]
        assert event.type == ExposureEventType.HEADLINE
        assert event.name is None
        assert event.start_date == datetime.datetime(2026, 1, 1)
        assert event.end_date == datetime.datetime(2026, 2, 1)
        # views_at(end=2026-02-01) - views_at(start - 1 day = 2025-12-31) = 30 - 5
        assert event.views_on_period == 25

    def test_headline_offer_event_without_end_date(self):
        headline = offers_factories.HeadlineOfferFactory(timespan=(datetime.datetime(2026, 1, 1),))

        response = GetOfferExposureResponseModel.build(headline.offer, CUMULATIVE_VIEWS)

        assert len(response.events) == 1
        event = response.events[0]
        assert event.type == ExposureEventType.HEADLINE
        assert event.start_date == datetime.datetime(2026, 1, 1)
        assert event.end_date is None
        # ongoing -> views_at(now=2026-06-01) - views_at(start - 1 day = 2025-12-31) = 105 - 5
        assert event.views_on_period == 100

    def test_highlight_event_with_end_date(self):
        offer = offers_factories.OfferFactory()
        highlight = highlights_factories.HighlightFactory(
            name="Mock Name",
            communication_date=datetime.date(2026, 2, 1),
            highlight_datespan=db_utils.make_inclusive_daterange(
                start=datetime.date(2026, 1, 1), end=datetime.date(2026, 7, 1)
            ),
        )
        criterion = criteria_factories.CriterionFactory(highlight=highlight)
        criteria_factories.OfferCriterionFactory(offerId=offer.id, criterionId=criterion.id)

        response = GetOfferExposureResponseModel.build(offer, CUMULATIVE_VIEWS)

        assert len(response.events) == 1
        event = response.events[0]
        assert event.type == ExposureEventType.HIGHLIGHT
        assert event.name == "Mock Name"
        # communication_date 2026-02-01 read as Paris midnight, then converted to naive UTC (winter: UTC+1)
        assert event.start_date == datetime.datetime(2026, 1, 31, 23, 0)
        # inclusive end 2026-07-01 read as Paris 23:59:59.999999, then converted to naive UTC (summer: UTC+2)
        assert event.end_date == datetime.datetime(2026, 7, 1, 21, 59, 59, 999999)
        # views_at(end=2026-07-01) - views_at(start - 1 day = 2026-01-30) = 200 - 10
        assert event.views_on_period == 190

    def test_highlight_event_uses_offer_timezone(self):
        venue = offerers_factories.VenueFactory(
            offererAddress__address__timezone="America/Martinique",
            offererAddress__address__departmentCode="972",
            offererAddress__address__postalCode="97200",
        )
        offer = offers_factories.OfferFactory(venue=venue)
        highlight = highlights_factories.HighlightFactory(
            name="Mock Name",
            communication_date=datetime.date(2026, 2, 1),
            highlight_datespan=db_utils.make_inclusive_daterange(
                start=datetime.date(2026, 1, 1), end=datetime.date(2026, 7, 1)
            ),
        )
        criterion = criteria_factories.CriterionFactory(highlight=highlight)
        criteria_factories.OfferCriterionFactory(offerId=offer.id, criterionId=criterion.id)

        response = GetOfferExposureResponseModel.build(offer, CUMULATIVE_VIEWS)

        assert len(response.events) == 1
        event = response.events[0]
        assert event.type == ExposureEventType.HIGHLIGHT
        # communication_date 2026-02-01 read as Martinique midnight, then converted to naive UTC (UTC-4)
        assert event.start_date == datetime.datetime(2026, 2, 1, 4, 0)
        # inclusive end 2026-07-01 read as Martinique 23:59:59.999999, then converted to naive UTC (UTC-4)
        assert event.end_date == datetime.datetime(2026, 7, 2, 3, 59, 59, 999999)
        # views_at(end=2026-07-02) - views_at(start - 1 day = 2026-01-31) = 200 - 10
        assert event.views_on_period == 190

    def test_highlight_event_with_future_start_date(self):
        offer = offers_factories.OfferFactory()
        highlight = highlights_factories.HighlightFactory(
            communication_date=datetime.date(2026, 9, 1),
            highlight_datespan=db_utils.make_inclusive_daterange(
                start=datetime.date(2026, 6, 1), end=datetime.date(2026, 12, 1)
            ),
        )
        criterion = criteria_factories.CriterionFactory(highlight=highlight)
        criteria_factories.OfferCriterionFactory(offerId=offer.id, criterionId=criterion.id)

        response = GetOfferExposureResponseModel.build(offer, CUMULATIVE_VIEWS)

        assert response.events == []

    def test_pro_advice_event(self):
        offer = offers_factories.OfferFactory()
        offers_factories.ProAdviceFactory(
            offer=offer,
            updatedAt=datetime.datetime(2026, 4, 1),
        )

        response = GetOfferExposureResponseModel.build(offer, CUMULATIVE_VIEWS)

        assert len(response.events) == 1
        event = response.events[0]
        assert event.type == ExposureEventType.PRO_ADVICE
        assert event.name is None
        assert event.start_date == datetime.datetime(2026, 4, 1)
        assert event.end_date is None
        # ongoing -> views_at(now=2026-06-01) - views_at(start - 1 day = 2026-03-31) = 105 - 45
        assert event.views_on_period == 60

    def test_returns_three_most_recent_events_sorted_by_start_date(self):
        offer = offers_factories.OfferFactory()
        offers_factories.HeadlineOfferFactory(
            offer=offer, timespan=(datetime.datetime(2026, 1, 1), datetime.datetime(2026, 2, 1))
        )
        offers_factories.HeadlineOfferFactory(
            offer=offer, timespan=(datetime.datetime(2026, 2, 1), datetime.datetime(2026, 3, 1))
        )
        highlight = highlights_factories.HighlightFactory(
            communication_date=datetime.date(2026, 3, 1),
            highlight_datespan=db_utils.make_inclusive_daterange(
                start=datetime.date(2026, 2, 1), end=datetime.date(2026, 4, 1)
            ),
        )
        criterion = criteria_factories.CriterionFactory(highlight=highlight)
        criteria_factories.OfferCriterionFactory(offerId=offer.id, criterionId=criterion.id)
        offers_factories.ProAdviceFactory(offer=offer, updatedAt=datetime.datetime(2026, 4, 1))

        response = GetOfferExposureResponseModel.build(offer, CUMULATIVE_VIEWS)

        assert len(response.events) == 3
        assert [event.type for event in response.events] == [
            ExposureEventType.PRO_ADVICE,
            ExposureEventType.HIGHLIGHT,
            ExposureEventType.HEADLINE,
        ]
