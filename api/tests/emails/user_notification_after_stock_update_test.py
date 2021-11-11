from datetime import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.emails.user_notification_after_stock_update import (
    retrieve_data_to_warn_user_after_stock_update_affecting_booking,
)


pytestmark = pytest.mark.usefixtures("db_session")


class RetrieveDataToWarnUserAfterStockUpdateAffectingBookingTest:
    def test_should_send_email_when_stock_date_have_been_changed(self):
        # Given
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime(2019, 8, 20, 12, 0, 0))
        booking = bookings_factories.BookingFactory(stock=stock)

        # When
        booking_info_for_mailjet = retrieve_data_to_warn_user_after_stock_update_affecting_booking(booking)

        # Then
        assert booking_info_for_mailjet == {
            "MJ-TemplateID": 1332139,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_name": booking.stock.offer.name,
                "user_first_name": booking.firstName,
                "venue_name": booking.venue.name,
                "event_date": "mardi 20 août 2019",
                "event_hour": "14h",
            },
        }
