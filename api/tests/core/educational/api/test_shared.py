import datetime

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import shared
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class SharedTest:
    def test_update_cancellation_limit_date_naive(self) -> None:
        now = datetime.datetime.utcnow()
        start = now + datetime.timedelta(days=35)
        stock = educational_factories.CollectiveStockFactory(startDatetime=start)
        booking = educational_factories.CollectiveBookingFactory(collectiveStock=stock)
        assert booking.cancellationLimitDate == start - datetime.timedelta(days=30)

        new_start_naive = now + datetime.timedelta(days=34)
        assert new_start_naive.tzinfo is None
        shared._update_collective_booking_cancellation_limit_date(booking, new_start_naive)

        booking = (
            db.session.query(educational_models.CollectiveBooking)
            .filter(educational_models.CollectiveBooking.id == booking.id)
            .one()
        )
        assert booking.cancellationLimitDate == new_start_naive - datetime.timedelta(days=30)

    def test_update_cancellation_limit_date_aware(self) -> None:
        now_aware = datetime.datetime.now(datetime.timezone.utc)
        now_naive = now_aware.replace(tzinfo=None)
        start = now_naive + datetime.timedelta(days=35)
        stock = educational_factories.CollectiveStockFactory(startDatetime=start)
        booking = educational_factories.CollectiveBookingFactory(collectiveStock=stock)
        assert booking.cancellationLimitDate == start - datetime.timedelta(days=30)

        new_start_aware = now_aware + datetime.timedelta(days=34)
        assert new_start_aware.tzinfo is datetime.timezone.utc
        shared._update_collective_booking_cancellation_limit_date(booking, new_start_aware)

        booking = (
            db.session.query(educational_models.CollectiveBooking)
            .filter(educational_models.CollectiveBooking.id == booking.id)
            .one()
        )
        assert booking.cancellationLimitDate == new_start_aware - datetime.timedelta(days=30)
