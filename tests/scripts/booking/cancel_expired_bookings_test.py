from datetime import datetime
from datetime import timedelta
from unittest import mock

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.users.factories import UserFactory
from pcapi.models import offer_type
from pcapi.repository import repository
from pcapi.scripts.booking.cancel_expired_bookings import cancel_expired_bookings


@pytest.mark.usefixtures("db_session")
class CancelExpiredBookingsTest:
    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_cancel_old_thing_that_can_expire_booking(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(type=str(offer_type.ThingType.LIVRE_EDITION))
        old_book_booking = BookingFactory(stock__offer__product=book, dateCreated=two_months_ago)

        cancel_expired_bookings()

        assert old_book_booking.isCancelled
        assert old_book_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp())
        assert old_book_booking.cancellationReason == BookingCancellationReasons.EXPIRED

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_not_cancel_new_thing_that_can_expire_booking(self, app) -> None:
        book = ProductFactory(type=str(offer_type.ThingType.LIVRE_EDITION))
        book_booking = BookingFactory(stock__offer__product=book)

        cancel_expired_bookings()

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

        cancel_expired_bookings()

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

        cancel_expired_bookings()

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

        cancel_expired_bookings()

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

        cancel_expired_bookings(batch_size=2)

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

        cancel_expired_bookings()

        assert old_guitar_booking.isCancelled
        assert old_guitar_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp())
        assert old_guitar_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert old_disc_booking.isCancelled
        assert old_disc_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp())
        assert old_disc_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert not old_audio_book_booking.isCancelled
        assert not old_audio_book_booking.cancellationDate
        assert not old_audio_book_booking.cancellationReason
