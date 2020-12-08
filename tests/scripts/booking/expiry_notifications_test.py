from datetime import datetime
from datetime import timedelta
import logging
from unittest import mock

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.offers.factories import ProductFactory
from pcapi.models import offer_type
from pcapi.repository import repository
from pcapi.scripts.booking.expiry_notifications import notify_offerers_of_expired_bookings
from pcapi.scripts.booking.expiry_notifications import notify_users_of_expired_bookings


@pytest.mark.usefixtures("db_session")
class NotifyUsersOfExpiredBookingsTest:
    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_log_notifications_of_todays_expired_bookings(self, app, caplog) -> None:
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

        notify_users_of_expired_bookings()

        assert (
            caplog.records[1].message
            == f"2 Users have been notified: [{expired_today_dvd_booking.user}, {expired_today_cd_booking.user}]"
        )
        assert str(expired_yesterday_painting_booking) not in caplog.text


@pytest.mark.usefixtures("db_session")
class NotifyOfferersOfExpiredBookingsTest:
    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    def should_log_notifications_of_todays_expired_bookings(self, app, caplog) -> None:
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

        notify_offerers_of_expired_bookings()

        assert (
            caplog.records[1].message
            == f"2 Offerers have been notified: [{expired_today_dvd_booking.stock.offer.venue.managingOfferer},"
            f" {expired_today_cd_booking.stock.offer.venue.managingOfferer}]"
        )
        assert str(expired_yesterday_painting_booking) not in caplog.text
