from datetime import datetime
from datetime import timezone

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.emails.user_warning_after_pro_booking_cancellation import (
    retrieve_data_to_warn_user_after_pro_booking_cancellation,
)


@pytest.mark.usefixtures("db_session")
class RetrieveDataToWarnUserAfterProBookingCancellationTest:
    def test_should_return_event_data_when_booking_is_on_an_event(self):
        # Given
        stock = offers_factories.EventStockFactory(
            beginningDatetime=datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        )
        booking = bookings_factories.IndividualBookingFactory(stock=stock, individualBooking__user__firstName="Georges")

        # When
        mailjet_data = retrieve_data_to_warn_user_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data == {
            "MJ-TemplateID": 1116690,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "can_book_again": 1,
                "event_date": "samedi 20 juillet 2019",
                "event_hour": "14h",
                "is_event": 1,
                "is_free_offer": 0,
                "is_online": 0,
                "is_thing": 0,
                "offer_name": booking.stock.offer.name,
                "offer_price": "10.00",
                "offerer_name": booking.offerer.name,
                "user_first_name": "Georges",
                "venue_name": booking.venue.name,
            },
        }

    def test_should_return_thing_data_when_booking_is_on_a_thing(self):
        # Given
        stock = offers_factories.ThingStockFactory()
        booking = bookings_factories.IndividualBookingFactory(stock=stock, individualBooking__user__firstName="Georges")

        # When
        mailjet_data = retrieve_data_to_warn_user_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data == {
            "MJ-TemplateID": 1116690,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "can_book_again": 1,
                "event_date": "",
                "event_hour": "",
                "is_event": 0,
                "is_free_offer": 0,
                "is_online": 0,
                "is_thing": 1,
                "offer_name": booking.stock.offer.name,
                "offer_price": "10.00",
                "offerer_name": booking.offerer.name,
                "user_first_name": "Georges",
                "venue_name": booking.venue.name,
            },
        }

    def test_should_return_thing_data_when_booking_is_on_an_online_offer(self):
        # Given
        stock = offers_factories.ThingStockFactory(offer__product=offers_factories.DigitalProductFactory())
        booking = bookings_factories.IndividualBookingFactory(stock=stock, individualBooking__user__firstName="Georges")

        # When
        mailjet_data = retrieve_data_to_warn_user_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data == {
            "MJ-TemplateID": 1116690,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "can_book_again": 1,
                "event_date": "",
                "event_hour": "",
                "is_event": 0,
                "is_free_offer": 0,
                "is_online": 1,
                "is_thing": 0,
                "offer_name": booking.stock.offer.name,
                "offer_price": "10.00",
                "offerer_name": booking.offerer.name,
                "user_first_name": "Georges",
                "venue_name": booking.venue.name,
            },
        }

    def test_should_not_display_the_price_when_booking_is_on_a_free_offer(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory(
            stock__price=0,
            individualBooking__user__firstName="Georges",
        )

        # When
        mailjet_data = retrieve_data_to_warn_user_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data["Vars"]["is_free_offer"] == 1
        assert mailjet_data["Vars"]["offer_price"] == "0.00"

    def test_should_display_the_price_multiplied_by_quantity_when_it_is_a_duo_offer(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory(
            amount=10,
            quantity=2,
            individualBooking__user__firstName="Georges",
        )

        # When
        mailjet_data = retrieve_data_to_warn_user_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data["Vars"]["is_free_offer"] == 0
        assert mailjet_data["Vars"]["offer_price"] == "20.00"
