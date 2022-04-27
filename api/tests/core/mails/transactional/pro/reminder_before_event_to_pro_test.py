from dataclasses import asdict
from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.reminder_before_event_to_pro import get_reminder_7_days_before_event_email_data
from pcapi.core.mails.transactional.pro.reminder_before_event_to_pro import send_reminder_7_days_before_event_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Reminder7DaysBeforeEventToProEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, bookingEmail="venue@bookingEmail.com")
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product, bookingEmail="offer@bookingEmail.com")
        stock = offers_factories.EventStockFactory(offer=offer, price=5, beginningDatetime=datetime(2022, 5, 1, 14, 10))
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)

        # When
        send_reminder_7_days_before_event_to_pro(stock)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "offer@bookingEmail.com"
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.REMINDER_7_DAYS_BEFORE_EVENT_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": product.name,
            "VENUE_NAME": venue.name,
            "EVENT_DATE": "dimanche 1 mai 2022",
            "EVENT_HOUR": "16h10",
            "BOOKING_COUNT": 3,
        }

    def test_sends_email_to_pro_venue_booking_email_when_offer_booking_email_is_missing(self):
        # Given
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, bookingEmail="venue@bookingEmail.com")
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product, bookingEmail=None)
        stock = offers_factories.EventStockFactory(offer=offer, price=5, beginningDatetime=datetime(2022, 5, 1, 14, 10))
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)

        # When
        send_reminder_7_days_before_event_to_pro(stock)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "venue@bookingEmail.com"
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.REMINDER_7_DAYS_BEFORE_EVENT_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": product.name,
            "VENUE_NAME": venue.name,
            "EVENT_DATE": "dimanche 1 mai 2022",
            "EVENT_HOUR": "16h10",
            "BOOKING_COUNT": 2,
        }

    def test_get_email_metadata(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, bookingEmail="venue@bookingEmail.com")
        product = offers_factories.EventProductFactory()
        offer = offers_factories.EventOfferFactory(venue=venue, product=product, bookingEmail="offer@bookingEmail.com")
        stock = offers_factories.EventStockFactory(offer=offer, price=5, beginningDatetime=datetime(2022, 3, 2, 14, 20))
        bookings_factories.BookingFactory(stock=stock)

        # When
        email_data = get_reminder_7_days_before_event_email_data(stock)

        assert email_data.template == TransactionalEmail.REMINDER_7_DAYS_BEFORE_EVENT_TO_PRO.value
        assert email_data.params == {
            "OFFER_NAME": product.name,
            "VENUE_NAME": venue.name,
            "EVENT_DATE": "mercredi 2 mars 2022",
            "EVENT_HOUR": "15h20",
            "BOOKING_COUNT": 1,
        }
