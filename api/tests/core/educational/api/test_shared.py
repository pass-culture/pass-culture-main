import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational.api import shared
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class SharedTest:
    def test_update_cancellation_limit_date_naive(self) -> None:
        now = date_utils.get_naive_utc_now()
        start = now + datetime.timedelta(days=35)
        stock = factories.CollectiveStockFactory(startDatetime=start)
        booking = factories.CollectiveBookingFactory(collectiveStock=stock)
        assert booking.cancellationLimitDate == start - datetime.timedelta(days=30)

        new_start_naive = now + datetime.timedelta(days=34)
        assert new_start_naive.tzinfo is None
        shared._update_collective_booking_cancellation_limit_date(booking, new_start_naive)

        assert booking.cancellationLimitDate == new_start_naive - datetime.timedelta(days=30)

    def test_update_cancellation_limit_date_aware(self) -> None:
        now_aware = datetime.datetime.now(datetime.timezone.utc)
        now_naive = now_aware.replace(tzinfo=None)
        start = now_naive + datetime.timedelta(days=35)
        stock = factories.CollectiveStockFactory(startDatetime=start)
        booking = factories.CollectiveBookingFactory(collectiveStock=stock)
        assert booking.cancellationLimitDate == start - datetime.timedelta(days=30)

        new_start_aware = now_aware + datetime.timedelta(days=34)
        assert new_start_aware.tzinfo is datetime.timezone.utc
        shared._update_collective_booking_cancellation_limit_date(booking, new_start_aware)

        assert booking.cancellationLimitDate == new_start_aware.replace(tzinfo=None) - datetime.timedelta(days=30)
