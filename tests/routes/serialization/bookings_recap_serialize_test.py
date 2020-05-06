from datetime import datetime

from flask import json

from domain.booking_recap.booking_recap import BookingRecap, BookingRecapStatus
from routes.serialization.bookings_recap_serialize import serialize_bookings_recap
from utils.date import format_into_ISO_8601


class SerializeBookingRecapTest:
    def test_should_return_json_with_all_parameters(self, app):
        # Given
        date = datetime.utcnow()
        bookings_recap = [
            BookingRecap(
                offer_name="Fondation",
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=date,
                booking_token="FOND",
                booking_status=BookingRecapStatus.validated
            ),
            BookingRecap(
                offer_name="Fondation",
                beneficiary_firstname="Golan",
                beneficiary_lastname="Trevize",
                beneficiary_email="golan.trevize@example.com",
                booking_date=date,
                booking_token="FOND",
                booking_status=BookingRecapStatus.booked
            )
        ]

        # When
        bookings = serialize_bookings_recap(bookings_recap)

        # Then
        response = json.loads(bookings.get_data().decode("utf-8"))
        expected_response = [
            {
                "stock": {
                    "offer_name": "Fondation",
                },
                "beneficiary": {
                    "lastname": "Seldon",
                    "firstname": "Hari",
                    "email": "hari.seldon@example.com",
                },
                "booking_date": format_into_ISO_8601(date),
                "booking_token": "FOND",
                "booking_status": "validated"
            },
            {
                "stock": {
                    "offer_name": "Fondation",
                },
                "beneficiary": {
                    "lastname": "Trevize",
                    "firstname": "Golan",
                    "email": "golan.trevize@example.com",
                },
                "booking_date": format_into_ISO_8601(date),
                "booking_token": "FOND",
                "booking_status": "booked"
            }
        ]
        assert response == expected_response
