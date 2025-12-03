from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.mails.transactional.pro.highlight_communication_to_pro import send_highlight_communication_email_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


pytestmark = pytest.mark.usefixtures("db_session")


class SendHighlightCommunicationEmailToProTest:
    def test_send_email_to_pro_user(self):
        venue = offerers_factories.VenueFactory(bookingEmail="venue@bookingEmail.com")
        offer = offers_factories.EventOfferFactory(venue=venue)

        send_highlight_communication_email_to_pro(offer)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == "venue@bookingEmail.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.HIGHLIGHT_COMMUNICATION_TO_PRO.value)
        assert mails_testing.outbox[0]["params"] == {"OFFER_NAME": offer.name}

    def test_send_email_to_pro_user_without_booking_email_should_send_0_email(self):
        venue = offerers_factories.VenueFactory(bookingEmail=None)
        offer = offers_factories.EventOfferFactory(venue=venue)

        send_highlight_communication_email_to_pro(offer)

        assert len(mails_testing.outbox) == 0
