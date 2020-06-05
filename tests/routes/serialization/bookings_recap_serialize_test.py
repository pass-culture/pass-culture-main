from datetime import datetime, timedelta

from domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from routes.serialization.bookings_recap_serialize import serialize_bookings_recap_paginated
from tests.domain_creators.generic_creators import create_domain_thing_booking_recap, create_domain_event_booking_recap
from utils.date import format_into_ISO_8601_with_timezone


class SerializeBookingRecapTest:
    def test_should_return_json_with_all_parameters_for_thing_stock(self, app):
        # Given
        booking_date = datetime(2020, 1, 1, 10, 0, 0)
        bookings_recap = [
            create_domain_thing_booking_recap(
                offer_name="Fondation",
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=booking_date,
                booking_token="FOND",
                booking_is_used=True,
            ),
            create_domain_thing_booking_recap(
                offer_name="Fondation",
                beneficiary_firstname="Golan",
                beneficiary_lastname="Trevize",
                beneficiary_email="golan.trevize@example.com",
                booking_date=booking_date,
                booking_token="FOND",
                booking_is_duo=True,
            )
        ]
        bookings_recap_paginated_response = BookingsRecapPaginated(
            bookings_recap=bookings_recap,
            page=0,
            pages=1,
            total=2
        )

        # When
        result = serialize_bookings_recap_paginated(bookings_recap_paginated_response)

        # Then
        bookings_recap = [
            {
                "stock": {
                    "type": "thing",
                    "offer_name": "Fondation",
                    "offer_isbn": None,
                },
                "beneficiary": {
                    "lastname": "Seldon",
                    "firstname": "Hari",
                    "email": "hari.seldon@example.com",
                },
                "booking_date": format_into_ISO_8601_with_timezone(booking_date),
                "booking_token": "FOND",
                "booking_status": "validated",
                "booking_is_duo": False,
                "venue_identifier": "AE",
            },
            {
                "stock": {
                    "type": "thing",
                    "offer_name": "Fondation",
                    "offer_isbn": None,
                },
                "beneficiary": {
                    "lastname": "Trevize",
                    "firstname": "Golan",
                    "email": "golan.trevize@example.com",
                },
                "booking_date": format_into_ISO_8601_with_timezone(booking_date),
                "booking_token": None,
                "booking_status": "booked",
                "booking_is_duo": True,
                "venue_identifier": "AE",
            }
        ]
        assert result['bookings_recap'] == bookings_recap
        assert result['page'] == 0
        assert result['pages'] == 1
        assert result['total'] == 2

    def test_should_return_json_with_event_date_additional_parameter_for_event_stock(self, app):
        # Given
        booking_date = datetime(2020, 1, 1, 10, 0, 0)
        day_after_booking_date = booking_date + timedelta(days=1)
        bookings_recap = [
            create_domain_event_booking_recap(
                offer_name="Cirque du soleil",
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=booking_date,
                booking_token="SOLEIL",
                event_beginning_datetime=day_after_booking_date,
            )
        ]
        bookings_recap_paginated_response = BookingsRecapPaginated(
            bookings_recap=bookings_recap,
            page=0,
            pages=1,
            total=2
        )

        # When
        results = serialize_bookings_recap_paginated(bookings_recap_paginated_response)

        # Then
        expected_response = [
            {
                "stock": {
                    "type": "event",
                    "offer_name": "Cirque du soleil",
                    "event_beginning_datetime": format_into_ISO_8601_with_timezone(day_after_booking_date),
                },
                "beneficiary": {
                    "lastname": "Seldon",
                    "firstname": "Hari",
                    "email": "hari.seldon@example.com",
                },
                "booking_date": format_into_ISO_8601_with_timezone(booking_date),
                "booking_token": "SOLEIL",
                "booking_status": "booked",
                "booking_is_duo": False,
                "venue_identifier": "AE",
            },
        ]
        assert results['bookings_recap'] == expected_response
        assert results['page'] == 0
        assert results['pages'] == 1
        assert results['total'] == 2

    def test_should_return_json_with_offer_isbn_additional_parameter_for_thing_stock(self, app):
        # Given
        booking_date = datetime(2020, 1, 1, 10, 0, 0)
        bookings_recap = [
            create_domain_thing_booking_recap(
                offer_name="Martine a la playa",
                offer_isbn='987654345678',
                beneficiary_firstname="Hari",
                beneficiary_lastname="Seldon",
                beneficiary_email="hari.seldon@example.com",
                booking_date=booking_date,
                booking_token="LUNE",
            )
        ]
        bookings_recap_paginated_response = BookingsRecapPaginated(
            bookings_recap=bookings_recap,
            page=0,
            pages=1,
            total=2
        )

        # When
        results = serialize_bookings_recap_paginated(bookings_recap_paginated_response)

        # Then
        expected_response = [
            {
                "stock": {
                    "type": "thing",
                    "offer_name": "Martine a la playa",
                    "offer_isbn": '987654345678',
                },
                "beneficiary": {
                    "lastname": "Seldon",
                    "firstname": "Hari",
                    "email": "hari.seldon@example.com",
                },
                "booking_date": format_into_ISO_8601_with_timezone(booking_date),
                "booking_token": None,
                "booking_status": "booked",
                "booking_is_duo": False,
                "venue_identifier": "AE",
            },
        ]
        assert results['bookings_recap'] == expected_response
        assert results['page'] == 0
        assert results['pages'] == 1
        assert results['total'] == 2
