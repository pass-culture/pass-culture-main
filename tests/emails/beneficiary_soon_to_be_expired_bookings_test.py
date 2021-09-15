from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.emails.beneficiary_soon_to_be_expired_bookings import (
    build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary,
)
from pcapi.emails.beneficiary_soon_to_be_expired_bookings import filter_books_bookings


@pytest.mark.usefixtures("db_session")
class BuildSoonToBeExpiredBookingsRecapEmailDataForBeneficiaryTest:
    def test_build_soon_to_be_expired_bookings_data(self, app):
        # Given
        beneficiary = BeneficiaryGrant18Factory(email="isasimov@example.com", firstName="ASIMOV")
        bookings = [
            BookingFactory(
                stock__offer__name="offre 1",
                stock__offer__venue__name="venue 1",
            ),
            BookingFactory(
                stock__offer__name="offre 2",
                stock__offer__venue__name="venue 2",
            ),
        ]

        # When
        data = build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
            beneficiary, bookings, days_before_cancel=7, days_from_booking=23
        )

        # Then
        assert data == {
            "Mj-TemplateID": 3095065,
            "Mj-TemplateLanguage": True,
            "Vars": {
                "user_firstName": "ASIMOV",
                "bookings": [
                    {"offer_name": "offre 1", "venue_name": "venue 1"},
                    {"offer_name": "offre 2", "venue_name": "venue 2"},
                ],
                "days_before_cancel": 7,
                "days_from_booking": 23,
            },
        }


@pytest.mark.usefixtures("db_session")
class FilterBooksBookingsTest:
    def test_filter_books_bookings_with_empty_list(self, app):
        # Given
        bookings = []

        # When
        books_bookings, other_bookings = filter_books_bookings(bookings)

        # Then
        assert books_bookings == []
        assert other_bookings == []

    def test_filter_books_bookings_with_one_book_and_one_other_booking(self, app):
        # Given
        book_booking = BookingFactory(
            stock__offer__name="offre 1",
            stock__offer__venue__name="venue 1",
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        other_booking = BookingFactory(
            stock__offer__name="offre 2",
            stock__offer__venue__name="venue 2",
            stock__offer__subcategoryId=subcategories.CINE_VENTE_DISTANCE.id,
        )

        bookings = [book_booking, other_booking]

        # When
        books_bookings, other_bookings = filter_books_bookings(bookings)

        # Then
        assert books_bookings == [book_booking]
        assert other_bookings == [other_booking]

    @patch(
        "pcapi.emails.beneficiary_soon_to_be_expired_bookings.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY_START_DATE",
        datetime(2021, 8, 5),
    )
    def test_filter_books_bookings_with_one_book_booked_before_new_expiry_delay_start(self):

        book_booking_1 = BookingFactory(
            stock__offer__name="offre 1",
            stock__offer__venue__name="venue 1",
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
            dateCreated=datetime(2021, 8, 3),
        )

        book_booking_2 = BookingFactory(
            stock__offer__name="offre 2",
            stock__offer__venue__name="venue 2",
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
            dateCreated=datetime(2021, 8, 6),
        )

        bookings = [book_booking_1, book_booking_2]

        books_bookings, other_bookings = filter_books_bookings(bookings)

        assert books_bookings[0] == book_booking_2
        assert other_bookings[0] == book_booking_1
