from datetime import datetime, timedelta

from flask import json

from tests.domain_creators.generic_creators import create_domain_thing_booking_recap, create_domain_event_booking_recap
from routes.serialization.bookings_recap_serialize import serialize_bookings_recap
from utils.date import format_into_ISO_8601


class SerializeBookingRecapTest:
    def test_should_return_json_with_all_parameters_for_thing_stock(self, app):
        # Given
        date = datetime.utcnow()
        bookings_recap = [
            create_domain_thing_booking_recap(
                offer_name="Fondation",
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=date,
                booking_token="FOND",
                booking_is_used=True,
            ),
            create_domain_thing_booking_recap(
                offer_name="Fondation",
                beneficiary_firstname="Golan",
                beneficiary_lastname="Trevize",
                beneficiary_email="golan.trevize@example.com",
                booking_date=date,
                booking_token="FOND",
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
                "booking_token": None,
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
            create_domain_event_booking_recap(
                offer_name="Cirque du soleil",
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=today,
                booking_token="SOLEIL",
                event_beginning_datetime=tomorrow,
                venue_department_code='75'
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
                    "venue_department_code": "75",
                },
                "beneficiary": {
                    "lastname": "Seldon",
                    "firstname": "Hari",
                    "email": "hari.seldon@example.com",
                },
                "booking_date": format_into_ISO_8601(today),
                "booking_token": "SOLEIL",
                "booking_status": "booked",
                "booking_is_duo": False,
            },
        ]
        assert response == expected_response
