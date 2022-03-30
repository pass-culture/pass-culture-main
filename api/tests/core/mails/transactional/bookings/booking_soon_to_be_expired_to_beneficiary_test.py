from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_soon_to_be_expired_to_beneficiary import (
    send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary,
)
from pcapi.core.mails.transactional.bookings.booking_soon_to_be_expired_to_beneficiary import _filter_books_bookings
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.factories import ProductFactory
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class FilterBooksBookingsTest:
    def test_filter_books_bookings_with_empty_list(self):
        # Given
        bookings = []

        # When
        books_bookings, other_bookings = _filter_books_bookings(bookings)

        # Then
        assert not books_bookings
        assert not other_bookings

    def test_filter_books_bookings_with_one_book_and_one_other_booking(self):
        # Given
        book_booking = BookingFactory(
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        other_booking = BookingFactory(
            stock__offer__subcategoryId=subcategories.CINE_VENTE_DISTANCE.id,
        )

        bookings = [book_booking, other_booking]

        # When
        books_bookings, other_bookings = _filter_books_bookings(bookings)

        # Then
        assert books_bookings == [book_booking]
        assert other_bookings == [other_booking]


class SendinblueSendSoonToBeExpiredBookingsEmailToBeneficiaryTest:
    def test_should_send_two_emails_to_beneficiary_when_they_have_soon_to_be_expired_bookings(
        self,
    ):
        # given
        now = datetime.utcnow()
        user = users_factories.BeneficiaryGrant18Factory(email="isasimov@example.com")
        created_5_days_ago = now - timedelta(days=5)
        created_23_days_ago = now - timedelta(days=23)

        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        soon_to_be_expired_book_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=book,
            dateCreated=created_5_days_ago,
            user=user,
        )

        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        soon_to_be_expired_dvd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=dvd,
            dateCreated=created_23_days_ago,
            user=user,
        )

        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        soon_to_be_expired_cd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=cd,
            dateCreated=created_23_days_ago,
            user=user,
        )

        # when
        send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary(
            user, [soon_to_be_expired_book_booking, soon_to_be_expired_cd_booking, soon_to_be_expired_dvd_booking]
        )

        # then
        assert len(mails_testing.outbox) == 2  # test number of emails sent
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.BOOKING_SOON_TO_BE_EXPIRED_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"] == {
            "FIRSTNAME": user.firstName,
            "BOOKINGS": [
                {
                    "offer_name": soon_to_be_expired_book_booking.stock.offer.name,
                    "venue_name": soon_to_be_expired_book_booking.stock.offer.venue.name,
                }
            ],
            "DAYS_BEFORE_CANCEL": 5,
            "DAYS_FROM_BOOKING": 5,
        }
        assert mails_testing.outbox[0].sent_data["To"] == "isasimov@example.com"

        assert (
            mails_testing.outbox[1].sent_data["template"]
            == TransactionalEmail.BOOKING_SOON_TO_BE_EXPIRED_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[1].sent_data["params"] == {
            "FIRSTNAME": user.firstName,
            "BOOKINGS": [
                {
                    "offer_name": soon_to_be_expired_cd_booking.stock.offer.name,
                    "venue_name": soon_to_be_expired_cd_booking.stock.offer.venue.name,
                },
                {
                    "offer_name": soon_to_be_expired_dvd_booking.stock.offer.name,
                    "venue_name": soon_to_be_expired_dvd_booking.stock.offer.venue.name,
                },
            ],
            "DAYS_BEFORE_CANCEL": 7,
            "DAYS_FROM_BOOKING": 23,
        }
        assert mails_testing.outbox[1].sent_data["To"] == "isasimov@example.com"
