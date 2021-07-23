from datetime import datetime
from datetime import timedelta
from unittest import mock

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import assert_num_queries
from pcapi.repository import repository
from pcapi.scripts.booking import handle_expired_bookings


@pytest.mark.usefixtures("db_session")
class CancelExpiredBookingsTest:
    def should_cancel_old_thing_that_can_expire_booking(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        old_book_booking = BookingFactory(stock__offer__product=book, dateCreated=two_months_ago)

        handle_expired_bookings.cancel_expired_bookings()

        assert old_book_booking.isCancelled
        assert old_book_booking.status is BookingStatus.CANCELLED
        assert old_book_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_book_booking.cancellationReason == BookingCancellationReasons.EXPIRED
        assert old_book_booking.stock.dnBookedQuantity == 0

    def should_not_cancel_new_thing_that_can_expire_booking(self, app) -> None:
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        book_booking = BookingFactory(stock__offer__product=book)

        handle_expired_bookings.cancel_expired_bookings()

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
        old_concert_booking = BookingFactory(
            dateCreated=two_months_ago, stock__beginningDatetime=tomorrow, stock__offer__product=concert
        )

        handle_expired_bookings.cancel_expired_bookings()

        assert not old_concert_booking.isCancelled
        assert old_concert_booking.status is not BookingStatus.CANCELLED
        assert not old_concert_booking.cancellationDate
        assert not old_concert_booking.cancellationReason

    def should_not_cancel_old_thing_that_cannot_expire_booking(self, app) -> None:
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        press_subscription = ProductFactory(subcategoryId=subcategories.ABO_PRESSE_EN_LIGNE.id)
        old_press_subscription_booking = BookingFactory(
            stock__offer__product=press_subscription, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_bookings()

        assert not old_press_subscription_booking.isCancelled
        assert old_press_subscription_booking.status is not BookingStatus.CANCELLED
        assert not old_press_subscription_booking.cancellationDate
        assert not old_press_subscription_booking.cancellationReason

    def should_not_update_cancelled_old_thing_that_can_expire_booking(self, app) -> None:
        fifty_days_ago = datetime.utcnow() - timedelta(days=50)
        forty_days_ago = datetime.utcnow() - timedelta(days=40)
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        old_book_booking = BookingFactory(
            stock__offer__product=book,
            dateCreated=fifty_days_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.BENEFICIARY,
        )
        old_book_booking.cancellationDate = forty_days_ago
        repository.save()

        handle_expired_bookings.cancel_expired_bookings()

        assert old_book_booking.isCancelled
        assert old_book_booking.status is BookingStatus.CANCELLED
        assert old_book_booking.cancellationDate == forty_days_ago
        assert old_book_booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

    def should_only_cancel_old_thing_that_can_expire_bookings_before_start_date(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        guitar = ProductFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
        )
        old_guitar_booking = BookingFactory(stock__offer__product=guitar, dateCreated=two_months_ago)
        disc = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        old_disc_booking = BookingFactory(stock__offer__product=disc, dateCreated=two_months_ago)
        audio_book = ProductFactory(subcategoryId=subcategories.LIVRE_AUDIO_PHYSIQUE.id)
        old_audio_book_booking = BookingFactory(stock__offer__product=audio_book, dateCreated=two_months_ago)

        handle_expired_bookings.cancel_expired_bookings()

        assert old_guitar_booking.isCancelled
        assert old_guitar_booking.status is BookingStatus.CANCELLED
        assert old_guitar_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_guitar_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert old_disc_booking.isCancelled
        assert old_disc_booking.status is BookingStatus.CANCELLED
        assert old_disc_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_disc_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert not old_audio_book_booking.isCancelled
        assert old_audio_book_booking.status is not BookingStatus.CANCELLED
        assert not old_audio_book_booking.cancellationDate
        assert not old_audio_book_booking.cancellationReason

    def test_queries_performance(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        BookingFactory.create_batch(size=10, stock__offer__product=book, dateCreated=two_months_ago)
        n_queries = (
            1  # select count
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
            handle_expired_bookings.cancel_expired_bookings(batch_size=3)


@pytest.mark.usefixtures("db_session")
class NotifyUsersOfExpiredBookingsTest:
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_bookings_recap_email_to_beneficiary")
    def should_notify_of_todays_expired_bookings(self, mocked_send_email_recap, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_today_dvd_booking = BookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        expired_today_cd_booking = BookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        expired_yesterday_painting_booking = BookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        expired_yesterday_painting_booking.cancellationDate = yesterday
        repository.save(expired_yesterday_painting_booking)

        handle_expired_bookings.notify_users_of_expired_bookings()

        assert mocked_send_email_recap.call_count == 2
        assert mocked_send_email_recap.call_args_list[0][0] == (
            expired_today_dvd_booking.user,
            [expired_today_dvd_booking],
        )
        assert mocked_send_email_recap.call_args_list[1][0] == (
            expired_today_cd_booking.user,
            [expired_today_cd_booking],
        )


@pytest.mark.usefixtures("db_session")
class NotifyOfferersOfExpiredBookingsTest:
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_bookings_recap_email_to_offerer")
    def should_notify_of_todays_expired_bookings(self, mocked_send_email_recap, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_today_dvd_booking = BookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        expired_today_cd_booking = BookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        expired_yesterday_painting_booking = BookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        expired_yesterday_painting_booking.cancellationDate = yesterday
        repository.save(expired_yesterday_painting_booking)

        handle_expired_bookings.notify_offerers_of_expired_bookings()

        assert mocked_send_email_recap.call_count == 2
        assert mocked_send_email_recap.call_args_list[0][0] == (
            expired_today_dvd_booking.stock.offer.venue.managingOfferer,
            [expired_today_dvd_booking],
        )
        assert mocked_send_email_recap.call_args_list[1][0] == (
            expired_today_cd_booking.stock.offer.venue.managingOfferer,
            [expired_today_cd_booking],
        )
