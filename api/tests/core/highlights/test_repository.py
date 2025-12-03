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
        offers = offers_factories.OfferFactory.create_batch(7)

        # ----------- Create criterion -----------
        # used to tag offers
        tag_first_highlight_today = criteria_factories.CriterionFactory(highlight=today_highlights[0])
        tag_second_highlight_today = criteria_factories.CriterionFactory(highlight=today_highlights[1])
        tag_highlight_not_today = criteria_factories.CriterionFactory(highlight=highlight)
        tag_not_for_highlight = criteria_factories.CriterionFactory(highlight=None)

        # ----------- Tag offers -----------
        # 1 offer tagged twice for different highlights that should be both used to send email (corresponding highlight communication date is today)
        criteria_factories.OfferCriterionFactory(criterionId=tag_first_highlight_today.id, offerId=offers[0].id)
        criteria_factories.OfferCriterionFactory(criterionId=tag_second_highlight_today.id, offerId=offers[0].id)

        # 1 offer tagged that should be used to send email (corresponding highlight communication date is today)
        criteria_factories.OfferCriterionFactory(criterionId=tag_second_highlight_today.id, offerId=offers[1].id)

        # 1 offer tagged that should not be used to send email (corresponding highlight communication date is not today)
        criteria_factories.OfferCriterionFactory(criterionId=tag_highlight_not_today.id, offerId=offers[3].id)

        # 1 offer tagged that should not be used to send email (corresponding highlight communication date is today but no request from cultural partner)
        criteria_factories.OfferCriterionFactory(criterionId=tag_second_highlight_today.id, offerId=offers[5].id)

        # 1 offer tagged but not for highlight
        criteria_factories.OfferCriterionFactory(criterionId=tag_not_for_highlight.id, offerId=offers[6].id)

        # ----------- Create highlight requests -----------
        # Two requests for the same tagged offer for two different highlights with communication date set to today,
        # Same venue.bookingEmail but different highlight
        request_for_offer_one_and_first_highlight_today = highlights_factories.HighlightRequestFactory(
            highlight=today_highlights[0], offer=offers[0]
        )
        request_for_offer_one_and_second_highlight_today = highlights_factories.HighlightRequestFactory(
            highlight=today_highlights[1], offer=offers[0]
        )

        # One request for a tagged offer for a highlight with communication date set to today, used to send one email
        request_for_second_offer_and_second_highlight_today = highlights_factories.HighlightRequestFactory(
            highlight=today_highlights[1], offer=offers[1]
        )

        # One request for a not tagged offer for a highlight with communication date set to today, not used to send one email
        highlights_factories.HighlightRequestFactory(highlight=today_highlights[1], offer=offers[2])

        # One request for a tagged offer for a highlight with communication date not set to today, not used to send one email
        highlights_factories.HighlightRequestFactory(highlight=highlight, offer=offers[3])

        # One request for a not tagged offer for a highlight with communication date not set to today, not used to send one email
        highlights_factories.HighlightRequestFactory(highlight=highlight, offer=offers[4])

        # One request for a tagged offer (not for highlight), not used to send one email
        highlights_factories.HighlightRequestFactory(highlight=today_highlights[1], offer=offers[6])

        today_highglight_requests = highlights_repository.get_today_highlight_requests()
        assert today_highglight_requests == [
            request_for_offer_one_and_first_highlight_today,
            request_for_offer_one_and_second_highlight_today,
            request_for_second_offer_and_second_highlight_today,
        ]
