from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
from unittest import mock

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.models import offer_type
from pcapi.repository import repository
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import notify_users_of_soon_to_be_expired_bookings


@pytest.mark.usefixtures("db_session")
class NotifyUsersOfSoonToBeExpiredBookingsTest:
    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    @mock.patch(
        "pcapi.scripts.booking.notify_soon_to_be_expired_bookings.send_soon_to_be_expired_bookings_recap_email_to_beneficiary"
    )
    def should_log_notifications_of_bookings_which_will_expire_in_7_days(self, mocked_email_recap, app, caplog) -> None:
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

        notify_users_of_soon_to_be_expired_bookings()

        assert (
            caplog.records[1].message
            == f"[notify_users_of_soon_to_be_expired_bookings] 2 Users have been notified: [{expire_in_7_days_dvd_booking.user}, {expire_in_7_days_cd_booking.user}]"
        )
        assert str(dont_expire_in_7_days_cd_booking) not in caplog.text

    @mock.patch("pcapi.core.bookings.conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE", datetime.utcnow())
    @mock.patch("pcapi.scripts.booking.notify_soon_to_be_expired_bookings.send_raw_email")
    @mock.patch(
        "pcapi.scripts.booking.notify_soon_to_be_expired_bookings.send_soon_to_be_expired_bookings_recap_email_to_beneficiary"
    )
    def should_call_email_service_for_bookings_which_will_expire_in_7_days(
        self, mocked_email_recap, mocked_send_raw_email, app, caplog
    ) -> None:
        # Given
        now = date.today()
        booking_date_23_days_ago = now - timedelta(days=23)
        booking_date_22_days_ago = now - timedelta(days=22)

        dvd = ProductFactory(type=str(offer_type.ThingType.AUDIOVISUEL))
        expire_in_7_days_dvd_booking = BookingFactory(
            stock__offer__product=dvd,
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

        # When
        notify_users_of_soon_to_be_expired_bookings()

        # Then
        mocked_email_recap.assert_called_once_with(
            expire_in_7_days_dvd_booking.user, [expire_in_7_days_dvd_booking], mocked_send_raw_email
        )
