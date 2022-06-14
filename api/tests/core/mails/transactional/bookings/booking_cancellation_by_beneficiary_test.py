from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories as booking_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary import (
    get_booking_cancellation_by_beneficiary_email_data,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary import (
    send_booking_cancellation_by_beneficiary_email,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory


@pytest.mark.usefixtures("db_session")
class SendSendiblueBeneficiaryBookingCancellationEmailTest:
    def test_should_called_send_email_with_valid_data(self):
        # given
        booking = booking_factories.IndividualBookingFactory()

        # when
        send_booking_cancellation_by_beneficiary_email(booking.individualBooking)

        # then
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == booking.individualBooking.user.email
        params_key_list = [
            "CAN_BOOK_AGAIN",
            "EVENT_DATE",
            "EVENT_HOUR",
            "IS_EVENT",
            "IS_FREE_OFFER",
            "OFFER_NAME",
            "OFFER_PRICE",
            "USER_FIRST_NAME",
            "OFFER_LINK",
        ]
        for params_key in params_key_list:
            assert params_key in mails_testing.outbox[0].sent_data["params"].keys()


@pytest.mark.usefixtures("db_session")
class MakeBeneficiaryBookingCancellationEmailSendinblueDataTest:
    def test_should_return_thing_data_when_booking_is_a_thing(self):
        # Given
        booking = booking_factories.CancelledIndividualBookingFactory(
            individualBooking__user=BeneficiaryGrant18Factory(email="fabien@example.com", firstName="Fabien"),
            stock=ThingStockFactory(
                price=10.20,
                beginningDatetime=datetime.utcnow() - timedelta(days=1),
                offer__name="Test thing name",
                offer__id=123456,
            ),
        )

        # When
        email_data = get_booking_cancellation_by_beneficiary_email_data(booking.individualBooking)

        # Then
        assert email_data.params == {
            "CAN_BOOK_AGAIN": True,
            "EVENT_DATE": None,
            "EVENT_HOUR": None,
            "IS_EVENT": False,
            "IS_EXTERNAL": False,
            "IS_FREE_OFFER": False,
            "OFFER_NAME": "Test thing name",
            "OFFER_PRICE": 10.20,
            "USER_FIRST_NAME": "Fabien",
            "OFFER_LINK": "https://webapp-v2.example.com/offre/123456",
        }

    @freeze_time("2019-11-26 18:29:20.891028")
    def test_should_return_event_data_when_booking_is_an_event(self):
        # Given
        booking = booking_factories.CancelledIndividualBookingFactory(
            individualBooking__user=BeneficiaryGrant18Factory(email="fabien@example.com", firstName="Fabien"),
            stock=EventStockFactory(
                price=10.20,
                beginningDatetime=datetime.utcnow(),
                offer__name="Test event name",
                offer__id=123456,
            ),
        )

        # When
        email_data = get_booking_cancellation_by_beneficiary_email_data(booking.individualBooking)

        # Then
        assert email_data.params == {
            "CAN_BOOK_AGAIN": True,
            "EVENT_DATE": "26 novembre 2019",
            "EVENT_HOUR": "19h29",
            "IS_EVENT": True,
            "IS_EXTERNAL": False,
            "IS_FREE_OFFER": False,
            "OFFER_NAME": "Test event name",
            "OFFER_PRICE": 10.20,
            "USER_FIRST_NAME": "Fabien",
            "OFFER_LINK": "https://webapp-v2.example.com/offre/123456",
        }

    def test_should_return_is_free_offer_when_offer_price_equals_to_zero(self):
        # Given
        booking = booking_factories.CancelledIndividualBookingFactory(stock__price=0)

        # When
        email_data = get_booking_cancellation_by_beneficiary_email_data(booking.individualBooking)

        # Then
        assert email_data.params["IS_FREE_OFFER"] is True

    def test_should_return_the_price_multiplied_by_quantity_when_it_is_a_duo_offer(self):
        # Given
        booking = booking_factories.CancelledIndividualBookingFactory(quantity=2, stock__price=10)

        # When
        email_data = get_booking_cancellation_by_beneficiary_email_data(booking.individualBooking)

        # Then
        assert email_data.params["OFFER_PRICE"] == 20.00
