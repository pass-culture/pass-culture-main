from dataclasses import asdict
from datetime import datetime

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.event_offer_postponed_confirmation_to_pro import (
    get_event_offer_postponed_confirmation_to_pro_email_data,
)
from pcapi.core.mails.transactional.pro.event_offer_postponed_confirmation_to_pro import (
    send_event_offer_postponement_confirmation_email_to_pro,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendEventOfferPosponedConfirmationToProEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, bookingEmail="venue@postponed.net")
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product, bookingEmail="test@bookingEmail.fr")
        stock = offers_factories.EventStockFactory(offer=offer, price=5, beginningDatetime=datetime(2022, 3, 1))

        # When
        send_event_offer_postponement_confirmation_email_to_pro(stock, booking_count=3)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "venue@postponed.net"
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": product.name,
            "VENUE_NAME": venue.name,
            "EVENT_DATE": "mardi 1 mars 2022",
            "BOOKING_COUNT": 3,
        }

    def test_get_email_metadata(self):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product, bookingEmail="test@bookingEmail.fr")
        stock = offers_factories.EventStockFactory(offer=offer, price=5, beginningDatetime=datetime(2022, 3, 2))

        # When
        email_data = get_event_offer_postponed_confirmation_to_pro_email_data(stock, booking_count=3)

        assert email_data.template == TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        assert email_data.params == {
            "OFFER_NAME": product.name,
            "VENUE_NAME": venue.name,
            "EVENT_DATE": "mercredi 2 mars 2022",
            "BOOKING_COUNT": 3,
        }
