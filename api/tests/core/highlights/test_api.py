import datetime
import logging

import pytest

from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.highlights import api as highlights_api
from pcapi.core.highlights import factories as highlights_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class SendEmailHighlightTest:
    def test_send_email_for_highlight_with_communication_date_set_to_today(self):
        today = datetime.date.today()

        # ----------- Create highlights -----------
        # with communication_date set to today
        today_highlight = highlights_factories.HighlightFactory.create(communication_date=today)

        # ----------- Create offers -----------
        offer = offers_factories.OfferFactory.create()

        # ----------- Create criterion -----------
        criterion = criteria_factories.CriterionFactory(highlight=today_highlight)

        # ----------- Tag offers -----------
        criteria_factories.OfferCriterionFactory(criterionId=criterion.id, offerId=offer.id)

        # ----------- Create highlight requests -----------
        highlights_factories.HighlightRequestFactory(highlight=today_highlight, offer=offer)

        with assert_num_queries(1):
            highlights_api.send_email_for_highlight_with_communication_date_set_to_today()

    def test_should_log_number_of_highlight_requests_for_today_communication(self, caplog):
        today = datetime.date.today()

        # ----------- Create highlights -----------
        # with communication_date set to today
        today_highlight = highlights_factories.HighlightFactory.create(communication_date=today)

        # ----------- Create offers -----------
        offer = offers_factories.OfferFactory.create()

        # ----------- Create criterion -----------
        criterion = criteria_factories.CriterionFactory(highlight=today_highlight)

        # ----------- Tag offers -----------
        criteria_factories.OfferCriterionFactory(criterionId=criterion.id, offerId=offer.id)

        # ----------- Create highlight requests -----------
        highlights_factories.HighlightRequestFactory(highlight=today_highlight, offer=offer)

        with caplog.at_level(logging.INFO):
            highlights_api.send_email_for_highlight_with_communication_date_set_to_today()

        assert caplog.records[0].message == "Found 1 highlight requests for today communcation"
