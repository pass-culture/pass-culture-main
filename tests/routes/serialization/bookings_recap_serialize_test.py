from datetime import datetime, timedelta

from flask import json

from domain.booking_recap.booking_recap import BookingRecap, BookingRecapStatus, EventBookingRecap
from routes.serialization.bookings_recap_serialize import serialize_bookings_recap
from utils.date import format_into_ISO_8601


class SerializeBookingRecapTest:
    def test_should_return_json_with_all_parameters_for_thing_stock(self, app):
        # Given
        date = datetime.utcnow()
        bookings_recap = [
            BookingRecap(
                offer_name="Fondation",
                offer_type='EventType.SPECTACLE_VIVANT',
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=date,
                booking_token="FOND",
                booking_status=BookingRecapStatus.validated,
                booking_is_duo=False,
            ),
            BookingRecap(
                offer_name="Fondation",
                offer_type='ThingType.LIVRE_EDITION',
                beneficiary_firstname="Golan",
                beneficiary_lastname="Trevize",
                beneficiary_email="golan.trevize@example.com",
                booking_date=date,
                booking_token="FOND",
                booking_status=BookingRecapStatus.booked,
                booking_is_duo=True,
            )
        ]

        # When
        bookings = serialize_bookings_recap(bookings_recap)

        # Then
        response = json.loads(bookings.get_data().decode("utf-8"))
        expected_response = [
            {
                "stock": {
                    "type": "thing",
                    "offer_name": "Fondation",
                },
                "beneficiary": {
                    "lastname": "Seldon",
                    "firstname": "Hari",
                    "email": "hari.seldon@example.com",
                },
                "booking_date": format_into_ISO_8601(date),
                "booking_token": "FOND",
                "booking_status": "validated",
                "booking_is_duo": False,
            },
            {
                "stock": {
                    "type": "thing",
                    "offer_name": "Fondation",
                },
                "beneficiary": {
                    "lastname": "Trevize",
                    "firstname": "Golan",
                    "email": "golan.trevize@example.com",
                },
                "booking_date": format_into_ISO_8601(date),
                "booking_token": "FOND",
                "booking_status": "booked",
                "booking_is_duo": True,
            }
        ]
        assert response == expected_response

    def test_should_return_json_with_event_date_additional_parameter_for_event_stock(self, app):
        # Given
        today = datetime.utcnow()
        tomorrow = today + timedelta(days=1)
        bookings_recap = [
            EventBookingRecap(
                offer_name="Cirque du soleil",
                offer_type='EventType.SPECTACLE_VIVANT',
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=today,
                booking_token="SOLEIL",
                booking_status=BookingRecapStatus.validated,
                event_beginning_datetime=tomorrow,
                booking_is_duo=False,
            )
        ]

        # When
        bookings = serialize_bookings_recap(bookings_recap)

        # Then
        response = json.loads(bookings.get_data().decode("utf-8"))
        expected_response = [
            {
                "stock": {
                    "type": "event",
                    "offer_name": "Cirque du soleil",
                    "event_beginning_datetime": format_into_ISO_8601(tomorrow),
                },
                "beneficiary": {
                    "lastname": "Seldon",
                    "firstname": "Hari",
                    "email": "hari.seldon@example.com",
                },
                "booking_date": format_into_ISO_8601(today),
                "booking_token": "SOLEIL",
                "booking_status": "validated",
                "booking_is_duo": False,
            },
        ]
        assert response == expected_response
