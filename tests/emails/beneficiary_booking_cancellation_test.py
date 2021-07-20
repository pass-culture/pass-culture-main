from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.users.factories import UserFactory
from pcapi.emails.beneficiary_booking_cancellation import make_beneficiary_booking_cancellation_email_data


@pytest.mark.usefixtures("db_session")
class MakeBeneficiaryBookingCancellationEmailDataTest:
    def test_should_return_thing_data_when_booking_is_a_thing(self):
        # Given
        booking = factories.BookingFactory(
            user=UserFactory(email="fabien@example.com", firstName="Fabien"),
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            stock=ThingStockFactory(
                price=10.2,
                beginningDatetime=datetime.now() - timedelta(days=1),
                offer__name="Test thing name",
                offer__id=123456,
            ),
        )

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data == {
            "Mj-TemplateID": 1091464,
            "Mj-TemplateLanguage": True,
            "Vars": {
                "can_book_again": 1,
                "event_date": "",
                "event_hour": "",
                "is_event": 0,
                "is_free_offer": 0,
                "offer_id": "AHREA",
                "offer_name": "Test thing name",
                "offer_price": "10.20",
                "user_first_name": "Fabien",
            },
        }

    @freeze_time("2019-11-26 18:29:20.891028")
    def test_should_return_event_data_when_booking_is_an_event(self):
        # Given
        booking = factories.BookingFactory(
            user=UserFactory(email="fabien@example.com", firstName="Fabien"),
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            stock=EventStockFactory(
                price=10.2,
                beginningDatetime=datetime.utcnow(),
                offer__name="Test event name",
                offer__id=123456,
            ),
        )

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data == {
            "Mj-TemplateID": 1091464,
            "Mj-TemplateLanguage": True,
            "Vars": {
                "can_book_again": 1,
                "event_date": "26 novembre 2019",
                "event_hour": "19h29",
                "is_event": 1,
                "is_free_offer": 0,
                "offer_id": "AHREA",
                "offer_name": "Test event name",
                "offer_price": "10.20",
                "user_first_name": "Fabien",
            },
        }

    def test_should_return_is_free_offer_when_offer_price_equals_to_zero(self):
        # Given
        booking = factories.BookingFactory(
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            stock=EventStockFactory(
                price=0,
            ),
        )

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data["Vars"]["is_free_offer"] == 1

    def test_should_return_the_price_multiplied_by_quantity_when_it_is_a_duo_offer(self):
        # Given
        booking = factories.BookingFactory(
            user=UserFactory(),
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            quantity=2,
            stock=ThingStockFactory(
                price=10,
            ),
        )

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data["Vars"]["offer_price"] == "20.00"
