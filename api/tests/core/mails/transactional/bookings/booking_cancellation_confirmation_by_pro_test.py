from dataclasses import asdict
from datetime import datetime

import pytest

from pcapi.core.bookings import factories as booking_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_cancellation_confirmation_by_pro import (
    get_booking_cancellation_confirmation_by_pro_email_data,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_confirmation_by_pro import (
    send_booking_cancellation_confirmation_by_pro_email,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import factories as offer_factories
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class BookingCancellationConfirmationByProEmailData:
    def test_should_return_email_data_with_correct_information_when_offer_is_an_event(self):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            publicName="John Doe", firstName="John", lastName="Doe", email="john@example.com"
        )
        offer = offer_factories.EventOfferFactory(
            venue__name="Venue name",
            product__name="My Event",
        )
        booking = booking_factories.IndividualBookingFactory(
            user=beneficiary,
            individualBooking__user=beneficiary,
            stock__offer=offer,
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20, 00),
            stock__price=12.52,
            quantity=2,
            token="12345",
        )
        bookings = [booking]

        # When
        email_data = get_booking_cancellation_confirmation_by_pro_email_data(bookings)

        # Then
        assert email_data.params == {
            "OFFER_NAME": "My Event",
            "VENUE_NAME": "Venue name",
            "PRICE": "12.52",
            "IS_EVENT": True,
            "EVENT_DATE": "09-Oct-2019",
            "EVENT_HOUR": "12h20",
            "QUANTITY": 2,
            "RESERVATIONS_NUMBER": 1,
        }

    def test_should_return_email_data_when_multiple_bookings_and_offer_is_a_thing(self):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            publicName="John Doe", firstName="John", lastName="Doe", email="john@example.com"
        )
        offer = offer_factories.ThingOfferFactory(
            venue__name="La petite librairie",
            venue__publicName="La grande librairie",
            product__name="Le récit de voyage",
        )
        booking = booking_factories.IndividualBookingFactory(
            user=beneficiary,
            individualBooking__user=beneficiary,
            stock__offer=offer,
            stock__price=0,
            token="12346",
            quantity=6,
        )

        other_beneficiary = users_factories.BeneficiaryGrant18Factory(
            publicName="James Bond", firstName="James", lastName="Bond", email="bond@example.com"
        )
        booking2 = booking_factories.IndividualBookingFactory(
            user=other_beneficiary,
            individualBooking__user=other_beneficiary,
            stock__offer=offer,
            stock__price=0,
            token="12345",
            quantity=1,
        )
        bookings = [booking, booking2]

        # When
        email_data = get_booking_cancellation_confirmation_by_pro_email_data(bookings)

        # Then
        assert email_data.params == {
            "OFFER_NAME": "Le récit de voyage",
            "VENUE_NAME": "La grande librairie",
            "PRICE": "Gratuit",
            "IS_EVENT": False,
            "EVENT_DATE": "",
            "EVENT_HOUR": "",
            "QUANTITY": 7,
            "RESERVATIONS_NUMBER": 2,
        }


@pytest.mark.usefixtures("db_session")
class SendOffererBookingsRecapEmailAfterOffererCancellationTest:
    def test_sends_to_offerer_administration(self):
        # Given
        booking = booking_factories.IndividualBookingFactory(stock__offer__bookingEmail="offerer@example.com")

        # When

        send_booking_cancellation_confirmation_by_pro_email([booking])

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.BOOKING_CANCELLATION_CONFIRMATION_BY_PRO.value
        )
