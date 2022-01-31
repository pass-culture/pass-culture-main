from datetime import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.mails.transactional.bookings.booking_postponed_by_pro_to_beneficiary import (
    get_booking_postponed_by_pro_to_beneficiary_email_data,
)
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.testing import override_features


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingPostponedByProToBeneficiaryTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_should_get_mailjet_email_data_when_stock_date_have_been_changed(self):
        # Given
        stock = EventStockFactory(beginningDatetime=datetime(2019, 8, 20, 12, 0, 0))
        booking = BookingFactory(stock=stock)

        # When
        booking_info_for_mailjet = get_booking_postponed_by_pro_to_beneficiary_email_data(booking)

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
                "booking_link": f"https://webapp-v2.example.com/reservation/{booking.id}/details",
            },
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_should_get_sendinblue_email_data_when_stock_date_have_been_changed(self):
        # Given
        stock = EventStockFactory(beginningDatetime=datetime(2019, 8, 20, 12, 0, 0))
        booking = BookingFactory(stock=stock)

        # When
        booking_info_for_sendinblue = get_booking_postponed_by_pro_to_beneficiary_email_data(booking)

        # Then
        assert booking_info_for_sendinblue.params == {
            "OFFER_NAME": booking.stock.offer.name,
            "FIRSTNAME": booking.firstName,
            "VENUE_NAME": booking.venue.name,
            "EVENT_DATE": "mardi 20 août 2019",
            "EVENT_HOUR": "14h",
            "BOOKING_LINK": f"https://webapp-v2.example.com/reservation/{booking.id}/details",
        }
