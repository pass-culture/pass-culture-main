from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
from unittest import mock

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.users.factories import UserFactory
from pcapi.models import offer_type
from pcapi.repository import repository
from pcapi.scripts.booking import handle_expired_bookings


@pytest.mark.usefixtures("db_session")
class CancelExpiredBookingsTest:
    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_cancel_old_thing_that_can_expire_booking(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(type=str(offer_type.ThingType.LIVRE_EDITION))
        old_book_booking = BookingFactory(stock__offer__product=book, dateCreated=two_months_ago)

        handle_expired_bookings.cancel_expired_bookings()

        assert old_book_booking.isCancelled
        assert old_book_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp())
        assert old_book_booking.cancellationReason == BookingCancellationReasons.EXPIRED

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_not_cancel_new_thing_that_can_expire_booking(self, app) -> None:
        book = ProductFactory(type=str(offer_type.ThingType.LIVRE_EDITION))
        book_booking = BookingFactory(stock__offer__product=book)

        handle_expired_bookings.cancel_expired_bookings()

        assert not book_booking.isCancelled
        assert not book_booking.cancellationDate
        assert not book_booking.cancellationReason

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_not_cancel_old_event_booking(self, app) -> None:
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        concert = ProductFactory(type=str(offer_type.EventType.MUSIQUE))
        old_concert_booking = BookingFactory(
            dateCreated=two_months_ago, stock__beginningDatetime=tomorrow, stock__offer__product=concert
        )

        handle_expired_bookings.cancel_expired_bookings()

        assert not old_concert_booking.isCancelled
        assert not old_concert_booking.cancellationDate
        assert not old_concert_booking.cancellationReason

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_not_cancel_old_thing_that_cannot_expire_booking(self, app) -> None:
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        press_subscription = ProductFactory(type=str(offer_type.ThingType.PRESSE_ABO))
        old_press_subscription_booking = BookingFactory(
            stock__offer__product=press_subscription, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_bookings()

        assert not old_press_subscription_booking.isCancelled
        assert not old_press_subscription_booking.cancellationDate
        assert not old_press_subscription_booking.cancellationReason

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_not_update_cancelled_old_thing_that_can_expire_booking(self, app) -> None:
        fifty_days_ago = datetime.utcnow() - timedelta(days=50)
        forty_days_ago = datetime.utcnow() - timedelta(days=40)
        book = ProductFactory(type=str(offer_type.ThingType.LIVRE_EDITION))
        old_book_booking = BookingFactory(
            stock__offer__product=book,
            dateCreated=fifty_days_ago,
            isCancelled=True,
            cancellationReason=BookingCancellationReasons.BENEFICIARY,
        )
        old_book_booking.cancellationDate = forty_days_ago
        repository.save()

        handle_expired_bookings.cancel_expired_bookings()

        assert old_book_booking.isCancelled
        assert old_book_booking.cancellationDate == forty_days_ago
        assert old_book_booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

    @mock.patch(
        "pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow() + timedelta(days=1)
    )
    def should_not_cancel_old_thing_that_can_expire_bookings_before_start_date(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(type=str(offer_type.ThingType.LIVRE_EDITION))
        user = UserFactory()
        BookingFactory.create_batch(size=5, stock__offer__product=book, user=user, dateCreated=two_months_ago)

        handle_expired_bookings.cancel_expired_bookings(batch_size=2)

        assert Booking.query.filter(Booking.isCancelled.is_(True)).count() == 0
        assert Booking.query.filter(Booking.cancellationDate.isnot(None)).count() == 0
        assert Booking.query.filter(Booking.cancellationReason.isnot(None)).count() == 0

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_only_cancel_old_thing_that_can_expire_bookings_before_start_date(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        guitar = ProductFactory(type=str(offer_type.ThingType.INSTRUMENT))
        old_guitar_booking = BookingFactory(stock__offer__product=guitar, dateCreated=two_months_ago)
        disc = ProductFactory(type=str(offer_type.ThingType.MUSIQUE))
        old_disc_booking = BookingFactory(stock__offer__product=disc, dateCreated=two_months_ago)
        audio_book = ProductFactory(type=str(offer_type.ThingType.LIVRE_AUDIO))
        old_audio_book_booking = BookingFactory(stock__offer__product=audio_book, dateCreated=two_months_ago)

        handle_expired_bookings.cancel_expired_bookings()

        assert old_guitar_booking.isCancelled
        assert old_guitar_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp())
        assert old_guitar_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert old_disc_booking.isCancelled
        assert old_disc_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp())
        assert old_disc_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert not old_audio_book_booking.isCancelled
        assert not old_audio_book_booking.cancellationDate
        assert not old_audio_book_booking.cancellationReason


@pytest.mark.usefixtures("db_session")
class NotifyUsersOfExpiredBookingsTest:
    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_raw_email")
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_bookings_recap_email_to_beneficiary")
    def should_notify_of_todays_expired_bookings(
        self, mocked_send_email_recap, mocked_send_raw_email, app, caplog
    ) -> None:
        caplog.set_level(logging.INFO)
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(type=str(offer_type.ThingType.AUDIOVISUEL))
        expired_today_dvd_booking = BookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            isCancelled=True,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(type=str(offer_type.ThingType.MUSIQUE))
        expired_today_cd_booking = BookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            isCancelled=True,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(type=str(offer_type.ThingType.OEUVRE_ART))
        expired_yesterday_painting_booking = BookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            isCancelled=True,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        expired_yesterday_painting_booking.cancellationDate = yesterday
        repository.save(expired_yesterday_painting_booking)

        handle_expired_bookings.notify_users_of_expired_bookings()

        assert (
            caplog.records[1].message
            == f"2 Users have been notified: [{expired_today_dvd_booking.user}, {expired_today_cd_booking.user}]"
        )
        assert str(expired_yesterday_painting_booking) not in caplog.text
        assert mocked_send_email_recap.call_args_list[0][0] == (
            expired_today_dvd_booking.user,
            [expired_today_dvd_booking],
            mocked_send_raw_email,
        )
        assert mocked_send_email_recap.call_args_list[1][0] == (
            expired_today_cd_booking.user,
            [expired_today_cd_booking],
            mocked_send_raw_email,
        )

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_log_notifications_of_bookings_which_will_expire_in_7_days(self, app, caplog) -> None:
        caplog.set_level(logging.INFO)
        now = date.today()
        booking_date_23_days_ago = now - timedelta(days=23)
        booking_date_22_days_ago = now - timedelta(days=22)

        dvd = ProductFactory(type=str(offer_type.ThingType.AUDIOVISUEL))
        expire_in_7_days_dvd_booking = BookingFactory(
            stock__offer__product=dvd,
            dateCreated=booking_date_23_days_ago,
            isCancelled=False,
        )
        cd = ProductFactory(type=str(offer_type.ThingType.MUSIQUE))
        expire_in_7_days_cd_booking = BookingFactory(
            stock__offer__product=cd,
            dateCreated=booking_date_23_days_ago,
            isCancelled=False,
        )
        non_expired_cd = ProductFactory(type=str(offer_type.ThingType.MUSIQUE))
        dont_expire_in_7_days_cd_booking = BookingFactory(
            stock__offer__product=non_expired_cd,
            dateCreated=booking_date_22_days_ago,
            isCancelled=False,
        )
        repository.save(dont_expire_in_7_days_cd_booking)

        handle_expired_bookings.notify_users_of_soon_to_be_expired_bookings()

        assert (
            caplog.records[1].message
            == f"[handle_soon_to_be_expired_bookings] 2 Users have been notified: [{expire_in_7_days_dvd_booking.user}, {expire_in_7_days_cd_booking.user}]"
        )
        assert str(dont_expire_in_7_days_cd_booking) not in caplog.text


@pytest.mark.usefixtures("db_session")
class NotifyOfferersOfExpiredBookingsTest:
    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_raw_email")
    @mock.patch("pcapi.scripts.booking.handle_expired_bookings.send_expired_bookings_recap_email_to_offerer")
    def should_notify_of_todays_expired_bookings(
        self, mocked_send_email_recap, mocked_send_raw_email, app, caplog
    ) -> None:
        caplog.set_level(logging.INFO)
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(type=str(offer_type.ThingType.AUDIOVISUEL))
        expired_today_dvd_booking = BookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            isCancelled=True,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(type=str(offer_type.ThingType.MUSIQUE))
        expired_today_cd_booking = BookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            isCancelled=True,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(type=str(offer_type.ThingType.OEUVRE_ART))
        expired_yesterday_painting_booking = BookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            isCancelled=True,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        expired_yesterday_painting_booking.cancellationDate = yesterday
        repository.save(expired_yesterday_painting_booking)

        handle_expired_bookings.notify_offerers_of_expired_bookings()

        assert (
            caplog.records[1].message
            == f"2 Offerers have been notified: [{expired_today_dvd_booking.stock.offer.venue.managingOfferer},"
            f" {expired_today_cd_booking.stock.offer.venue.managingOfferer}]"
        )
        assert str(expired_yesterday_painting_booking) not in caplog.text
        assert mocked_send_email_recap.call_args_list[0][0] == (
            expired_today_dvd_booking.stock.offer.venue.managingOfferer,
            [expired_today_dvd_booking],
            mocked_send_raw_email,
        )
        assert mocked_send_email_recap.call_args_list[1][0] == (
            expired_today_cd_booking.stock.offer.venue.managingOfferer,
            [expired_today_cd_booking],
            mocked_send_raw_email,
        )
