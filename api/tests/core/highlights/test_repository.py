import datetime

import pytest

from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.highlights import factories as highlights_factories
from pcapi.core.highlights import repository as highlights_repository
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import db as db_utils


pytestmark = pytest.mark.usefixtures("db_session")


class GetAvailableHighlightTest:
    def test_get_available_highlights(self):
        today = datetime.date.today()
        available_highlight = highlights_factories.HighlightFactory(
            availability_datespan=db_utils.make_inclusive_daterange(
                start=today - datetime.timedelta(days=10), end=today
            ),
        )
        unavailable_highlight = highlights_factories.HighlightFactory(
            availability_datespan=db_utils.make_inclusive_daterange(
                start=today - datetime.timedelta(days=10), end=today - datetime.timedelta(days=8)
            )
        )
        available_highlights = highlights_repository.get_available_highlights()
        assert available_highlight in available_highlights
        assert unavailable_highlight not in available_highlights


class GetTodayHighlightRequestsTest:
    def test_get_today_highlight_requests(self):
        today = datetime.date.today()

        # ----------- Create highlights -----------
        # with communication_date set to today
        today_highlights = highlights_factories.HighlightFactory.create_batch(2, communication_date=today)
        # with different communication_date
        highlight = highlights_factories.HighlightFactory(communication_date=today + datetime.timedelta(days=2))

        # ----------- Create offers -----------
        offers = offers_factories.OfferFactory.create_batch(6)

        # ----------- Create criterion -----------
        # used to tag offers
        criterion = criteria_factories.CriterionFactory(highlight=today_highlights[0])
        criterion1 = criteria_factories.CriterionFactory(highlight=today_highlights[1])
        criterion2 = criteria_factories.CriterionFactory(highlight=highlight)

        # ----------- Tag offers -----------
        # 2 offers tagged that should be used to send email (corresponding highlight communication date is today)
        criteria_factories.OfferCriterionFactory(criterionId=criterion.id, offerId=offers[0].id)
        criteria_factories.OfferCriterionFactory(criterionId=criterion.id, offerId=offers[1].id)

        # 1 offer tagged that should be used to send email (tagged for another highlight)
        criteria_factories.OfferCriterionFactory(criterionId=criterion1.id, offerId=offers[0].id)

        # 1 offer tagged that should not be used to send email (corresponding highlight communication date is not today)
        criteria_factories.OfferCriterionFactory(criterionId=criterion2.id, offerId=offers[3].id)

        # 1 offer tagged that should not be used to send email (corresponding highlight communication date is today but no request from cultural partner)
        criteria_factories.OfferCriterionFactory(criterionId=criterion2.id, offerId=offers[5].id)

        # ----------- Create highlight requests -----------
        # Two requests for the same tagged offer for two different highlights with communication date set to today,
        # Same venue.bookingEmail but different highlight
        today_request1 = highlights_factories.HighlightRequestFactory(highlight=today_highlights[0], offer=offers[0])
        today_request11 = highlights_factories.HighlightRequestFactory(highlight=today_highlights[1], offer=offers[0])

        # One request for a tagged offer for a highlight with communication date set to today, used to send one email
        today_request3 = highlights_factories.HighlightRequestFactory(highlight=today_highlights[1], offer=offers[1])

        # One request for a not tagged offer for a highlight with communication date set to today, not used to send one email
        highlights_factories.HighlightRequestFactory(highlight=today_highlights[1], offer=offers[2])

        # One request for a tagged offer for a highlight with communication date not set to today, not used to send one email
        highlights_factories.HighlightRequestFactory(highlight=highlight, offer=offers[3])

        # One request for a not tagged offer for a highlight with communication date not set to today, not used to send one email
        highlights_factories.HighlightRequestFactory(highlight=highlight, offer=offers[4])

        today_highglight_requests = highlights_repository.get_today_highlight_requests()
        assert today_highglight_requests == [today_request1, today_request11, today_request3]
