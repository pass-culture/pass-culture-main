from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.users.factories import UserFactory
from pcapi.emails.beneficiary_booking_cancellation import make_beneficiary_booking_cancellation_email_data
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class MakeBeneficiaryBookingCancellationEmailDataTest:
    @patch("pcapi.emails.beneficiary_booking_cancellation.format_environment_for_email", return_value="")
    def test_should_return_thing_data_when_booking_is_a_thing(self, mock_format_environment_for_email):
        # Given
        booking = factories.BookingFactory(
            user=UserFactory(email="fabien@example.com", firstName="Fabien"),
            isCancelled=True,
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
            "FromEmail": "support@example.com",
            "Mj-TemplateID": 1091464,
            "Mj-TemplateLanguage": True,
            "To": "fabien@example.com",
            "Vars": {
                "env": "",
                "event_date": "",
                "event_hour": "",
                "is_event": 0,
                "is_free_offer": 0,
                "mediation_id": "vide",
                "offer_id": "AHREA",
                "offer_name": "Test thing name",
                "offer_price": "10.20",
                "user_first_name": "Fabien",
            },
        }

    @freeze_time("2019-11-26 18:29:20.891028")
    @patch("pcapi.emails.beneficiary_booking_cancellation.format_environment_for_email", return_value="-testing")
    def test_should_return_event_data_when_booking_is_an_event(self, mock_format_environment_for_email):
        # Given
        booking = factories.BookingFactory(
            user=UserFactory(email="fabien@example.com", firstName="Fabien"),
            isCancelled=True,
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
            "FromEmail": "support@example.com",
            "Mj-TemplateID": 1091464,
            "Mj-TemplateLanguage": True,
            "To": "fabien@example.com",
            "Vars": {
                "env": "-testing",
                "event_date": "26 novembre",
                "event_hour": "19h29",
                "is_event": 1,
                "is_free_offer": 0,
                "mediation_id": "vide",
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
            stock=EventStockFactory(
                price=0,
            ),
        )

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data["Vars"]["is_free_offer"] == 1

    def test_should_return_with_an_id_of_mediation(self):
        # Given
        booking = factories.BookingFactory(
            user=UserFactory(),
            isCancelled=True,
            stock=ThingStockFactory(
                price=0,
            ),
        )
        mediation = MediationFactory(thumbCount=1, offer=booking.stock.offer)

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data["Vars"]["mediation_id"] == humanize(mediation.id)

    def test_should_return_the_price_multiplied_by_quantity_when_it_is_a_duo_offer(self):
        # Given
        booking = factories.BookingFactory(
            user=UserFactory(),
            isCancelled=True,
            quantity=2,
            stock=ThingStockFactory(
                price=10,
            ),
        )

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data["Vars"]["offer_price"] == "20.00"
