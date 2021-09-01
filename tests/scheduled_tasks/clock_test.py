from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.factories import EventStockFactory
from pcapi.notifications.push import testing
from pcapi.scheduled_tasks.clock import pc_send_tomorrow_events_notifications


@pytest.mark.usefixtures("db_session")
def test_pc_send_tomorrow_events_notifications_only_to_individual_bookings_users(app):
    """
    Test that each stock that is linked to an offer that occurs tomorrow and
    creates a job that will send a notification to all of the stock's users
    with a valid (not cancelled) booking, for individual bookings only.
    """
    tomorrow = datetime.now() + timedelta(days=1)
    stock_tomorrow = EventStockFactory(beginningDatetime=tomorrow, offer__name="my_offer")

    begin = datetime.now() + timedelta(days=7)
    stock_next_week = EventStockFactory(beginningDatetime=begin)

    bookings_tomorrow = IndividualBookingFactory.create_batch(2, stock=stock_tomorrow, isCancelled=False)
    BookingFactory.create_batch(2, stock=stock_tomorrow, isCancelled=True, status=BookingStatus.CANCELLED)
    BookingFactory.create_batch(2, stock=stock_next_week, isCancelled=False)
    EducationalBookingFactory.create_batch(2, stock=stock_tomorrow, isCancelled=False)

    pc_send_tomorrow_events_notifications(app)

    assert len(testing.requests) == 1
    assert all(data["message"]["title"] == "my_offer, c'est demain !" for data in testing.requests)

    user_ids = set()
    for data in testing.requests:
        for user_id in data["user_ids"]:
            user_ids.add(user_id)

    expected_user_ids = {booking.individualBooking.userId for booking in bookings_tomorrow}
    assert user_ids == expected_user_ids
