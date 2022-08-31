from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.mails.transactional.bookings.booking_postponed_by_pro_to_beneficiary import (
    get_booking_postponed_by_pro_to_beneficiary_email_data,
)
from pcapi.core.offers.factories import EventStockFactory


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingPostponedByProToBeneficiaryTest:
    def test_should_get_sendinblue_email_data_when_stock_date_have_been_changed(self):
        # Given
        stock = EventStockFactory(beginningDatetime=datetime(2019, 8, 20, 12, 0, 0))
        booking = bookings_factories.IndividualBookingFactory(stock=stock)

        # When
        booking_info_for_sendinblue = get_booking_postponed_by_pro_to_beneficiary_email_data(booking)

        # Then
        assert booking_info_for_sendinblue.params == {
            "OFFER_NAME": booking.stock.offer.name,
            "FIRSTNAME": booking.firstName,
            "VENUE_NAME": booking.venue.name,
            "IS_EXTERNAL": False,
            "EVENT_DATE": "mardi 20 août 2019",
            "EVENT_HOUR": "14h",
            "BOOKING_LINK": f"https://webapp-v2.example.com/reservation/{booking.id}/details",
        }
