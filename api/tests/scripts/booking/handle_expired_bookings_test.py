from datetime import datetime
from datetime import timedelta
from unittest import mock

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import assert_num_queries
from pcapi.scripts.booking import handle_expired_bookings


pytestmark = pytest.mark.usefixtures("db_session")


class CancelExpiredBookingsTest:
    def test_should_cancel_old_thing_that_can_expire_booking(self, app) -> None:
        now = datetime.utcnow()
        eleven_days_ago = now - timedelta(days=11)
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        old_book_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=book, dateCreated=eleven_days_ago
        )
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        old_dvd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=dvd, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_book_booking.isCancelled
        assert old_book_booking.status is BookingStatus.CANCELLED
        assert old_book_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_book_booking.cancellationReason == BookingCancellationReasons.EXPIRED
        assert old_book_booking.stock.dnBookedQuantity == 0

        assert old_dvd_booking.isCancelled
        assert old_dvd_booking.status is BookingStatus.CANCELLED
        assert old_dvd_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_dvd_booking.cancellationReason == BookingCancellationReasons.EXPIRED
        assert old_dvd_booking.stock.dnBookedQuantity == 0

    def should_not_cancel_new_thing_that_can_expire_booking(self, app) -> None:
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        book_booking = booking_factories.BookingFactory(stock__offer__product=book)

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert not book_booking.isCancelled
        assert book_booking.status is not BookingStatus.CANCELLED
        assert not book_booking.cancellationDate
        assert not book_booking.cancellationReason

    def should_not_cancel_old_event_booking(self, app) -> None:
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        concert = ProductFactory(
            subcategoryId=subcategories.CONCERT.id,
        )
        old_concert_booking = booking_factories.BookingFactory(
            dateCreated=two_months_ago, stock__beginningDatetime=tomorrow, stock__offer__product=concert
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert not old_concert_booking.isCancelled
        assert old_concert_booking.status is not BookingStatus.CANCELLED
        assert not old_concert_booking.cancellationDate
        assert not old_concert_booking.cancellationReason

    def should_not_cancel_old_thing_that_cannot_expire_booking(self, app) -> None:
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        press_subscription = ProductFactory(subcategoryId=subcategories.ABO_PRESSE_EN_LIGNE.id)
        old_press_subscription_booking = booking_factories.BookingFactory(
            stock__offer__product=press_subscription, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert not old_press_subscription_booking.isCancelled
        assert old_press_subscription_booking.status is not BookingStatus.CANCELLED
        assert not old_press_subscription_booking.cancellationDate
        assert not old_press_subscription_booking.cancellationReason

    def should_not_update_cancelled_old_thing_that_can_expire_booking(self, app) -> None:
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        old_book_booking = booking_factories.CancelledIndividualBookingFactory(stock__offer__product=book)
        initial_cancellation_date = old_book_booking.cancellationDate

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_book_booking.isCancelled
        assert old_book_booking.status is BookingStatus.CANCELLED
        assert old_book_booking.cancellationDate == initial_cancellation_date
        assert old_book_booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

    def should_only_cancel_old_thing_that_can_expire_bookings_before_start_date(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        guitar = ProductFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
        )
        old_guitar_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=guitar, dateCreated=two_months_ago
        )
        disc = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        old_disc_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=disc, dateCreated=two_months_ago
        )
        vod = ProductFactory(subcategoryId=subcategories.VOD.id)
        old_vod_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=vod, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_guitar_booking.isCancelled
        assert old_guitar_booking.status is BookingStatus.CANCELLED
        assert old_guitar_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_guitar_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert old_disc_booking.isCancelled
        assert old_disc_booking.status is BookingStatus.CANCELLED
        assert old_disc_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_disc_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert not old_vod_booking.isCancelled
        assert old_vod_booking.status is not BookingStatus.CANCELLED
        assert not old_vod_booking.cancellationDate
        assert not old_vod_booking.cancellationReason

    def test_should_cancel_pending_dated_educational_booking_when_confirmation_limit_date_has_passed(self, app) -> None:
        # Given
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        expired_pending_educational_booking: Booking = booking_factories.PendingEducationalBookingFactory(
            educationalBooking__confirmationLimitDate=yesterday
        )

        # When
        handle_expired_bookings.cancel_expired_educational_bookings()

        # Then
        assert expired_pending_educational_booking.status == BookingStatus.CANCELLED
        assert expired_pending_educational_booking.cancellationDate.timestamp() == pytest.approx(
            datetime.utcnow().timestamp(), rel=1
        )
        assert expired_pending_educational_booking.cancellationReason == BookingCancellationReasons.EXPIRED

    def test_should_not_cancel_confirmed_dated_educational_booking_when_confirmation_limit_date_has_passed(
        self, app
    ) -> None:
        # Given
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        confirmed_educational_booking: Booking = booking_factories.EducationalBookingFactory(
            educationalBooking__confirmationLimitDate=yesterday
        )

        # When
        handle_expired_bookings.cancel_expired_educational_bookings()

        # Then
        assert confirmed_educational_booking.status == BookingStatus.CONFIRMED

    def test_should_not_cancel_pending_dated_educational_booking_when_confirmation_limit_date_has_not_passed(
        self, app
    ) -> None:
        # Given
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        pending_educational_booking: Booking = booking_factories.PendingEducationalBookingFactory(
            educationalBooking__confirmationLimitDate=tomorrow
        )

        # When
        handle_expired_bookings.cancel_expired_educational_bookings()

        # Then
        assert pending_educational_booking.status == BookingStatus.PENDING

    def test_should_not_cancel_pending_dated_educational_booking_when_confirmation_limit_date_has_not_passed_and_booking_more_than_30_days_old(
        self, app
    ) -> None:
        # Given
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        old_date = now - timedelta(days=40)
        pending_educational_booking: Booking = booking_factories.PendingEducationalBookingFactory(
            educationalBooking__confirmationLimitDate=tomorrow, dateCreated=old_date
        )

        # When
        handle_expired_bookings.cancel_expired_educational_bookings()

        # Then
        assert pending_educational_booking.status == BookingStatus.PENDING

    def test_handle_expired_bookings_should_cancel_expired_individual_and_educational_bookings(self, app) -> None:
        # Given
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        two_months_ago = now - timedelta(days=60)
        tomorrow = now + timedelta(days=1)

        expired_pending_educational_booking: Booking = booking_factories.PendingEducationalBookingFactory(
            educationalBooking__confirmationLimitDate=yesterday
        )
        non_expired_pending_educational_booking: Booking = booking_factories.PendingEducationalBookingFactory(
            educationalBooking__confirmationLimitDate=tomorrow
        )

        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_individual_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=dvd, dateCreated=two_months_ago
        )

        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        book_individual_recent_booking = booking_factories.IndividualBookingFactory(stock__offer__product=book)

        # When
        handle_expired_bookings.handle_expired_bookings()

        # Then
        assert expired_pending_educational_booking.status == BookingStatus.CANCELLED
        assert expired_individual_booking.status == BookingStatus.CANCELLED
        assert book_individual_recent_booking.status != BookingStatus.CANCELLED
        assert non_expired_pending_educational_booking.status == BookingStatus.PENDING

    def test_queries_performance_individual_bookings(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        booking_factories.IndividualBookingFactory.create_batch(
            size=10, stock__offer__product=book, dateCreated=two_months_ago
        )
        n_queries = (
            +1  # select count
            + 1  # select initial booking ids
            + 1  # release savepoint/COMMIT
            + 4
            * (
                1  # update
                + 1  # release savepoint/COMMIT
                + 1  # select stock
                + 1  # recompute dnBookedQuantity
                + 1  # select next ids
            )
        )

        with assert_num_queries(n_queries):
            handle_expired_bookings.cancel_expired_individual_bookings(batch_size=3)

    def test_queries_performance_educational_bookings(self, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        booking_factories.PendingEducationalBookingFactory.create_batch(
            size=10, educationalBooking__confirmationLimitDate=yesterday
        )
        n_queries = (
            +1  # select count
            + 1  # select initial booking ids
            + 1  # release savepoint/COMMIT
            + 4
            * (
                1  # update
                + 1  # release savepoint/COMMIT
                + 1  # select stock
                + 1  # recompute dnBookedQuantity
                + 1  # select next ids
            )
        )

        with assert_num_queries(n_queries):
            handle_expired_bookings.cancel_expired_educational_bookings(batch_size=3)


class NotifyUsersOfExpiredBookingsTest:
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_bookings_recap_email_to_beneficiary")
    def should_notify_of_todays_expired_bookings(self, mocked_send_email_recap, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_today_dvd_booking = booking_factories.CancelledIndividualBookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        expired_today_cd_booking = booking_factories.CancelledIndividualBookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        _expired_yesterday_booking = booking_factories.CancelledIndividualBookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
            cancellationDate=yesterday,
        )

        handle_expired_bookings.notify_users_of_expired_individual_bookings()

        assert mocked_send_email_recap.call_count == 2
        assert mocked_send_email_recap.call_args_list[0][0] == (
            expired_today_dvd_booking.individualBooking.user,
            [expired_today_dvd_booking.individualBooking.booking],
        )
        assert mocked_send_email_recap.call_args_list[1][0] == (
            expired_today_cd_booking.individualBooking.user,
            [expired_today_cd_booking.individualBooking.booking],
        )

    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_bookings_recap_email_to_beneficiary")
    def test_should_not_notify_of_todays_expired_educational_bookings(self, mocked_send_email_recap, app) -> None:
        # Given
        now = datetime.utcnow()
        long_ago = now - timedelta(days=31)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        booking_factories.EducationalBookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )

        # When
        handle_expired_bookings.notify_users_of_expired_individual_bookings()

        # Then
        assert not mocked_send_email_recap.called


class NotifyOfferersOfExpiredBookingsTest:
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_individual_bookings_recap_email_to_offerer")
    def test_should_notify_of_todays_expired_individual_bookings(self, mocked_send_email_recap, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_today_dvd_booking = booking_factories.CancelledIndividualBookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        expired_today_cd_booking = booking_factories.CancelledIndividualBookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        _expired_yesterday_booking = booking_factories.CancelledIndividualBookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
            cancellationDate=yesterday,
        )

        handle_expired_bookings.notify_offerers_of_expired_individual_bookings()

        assert mocked_send_email_recap.call_count == 2
        assert mocked_send_email_recap.call_args_list[0][0] == (
            expired_today_dvd_booking.offerer,
            [expired_today_dvd_booking.individualBooking.booking],
        )
        assert mocked_send_email_recap.call_args_list[1][0] == (
            expired_today_cd_booking.offerer,
            [expired_today_cd_booking.individualBooking.booking],
        )

    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_individual_bookings_recap_email_to_offerer")
    def test_should_not_notify_of_todays_expired_educational_bookings(self, mocked_send_email_recap, app) -> None:
        # Given
        now = datetime.utcnow()
        long_ago = now - timedelta(days=31)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        booking_factories.EducationalBookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )

        # Given
        handle_expired_bookings.notify_offerers_of_expired_individual_bookings()

        # Then
        assert not mocked_send_email_recap.called
