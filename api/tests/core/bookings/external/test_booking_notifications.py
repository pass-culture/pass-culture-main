from datetime import timedelta

import pytest
import time_machine

from pcapi.core.bookings import constants
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.external.booking_notifications import notify_users_bookings_not_retrieved
from pcapi.core.bookings.external.booking_notifications import send_today_events_notifications_metropolitan_france
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.notifications.push import testing
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
# Set time to evening so that `send_today_events_notifications_metropolitan_france()`
# finds test stock in its `13:00 - 24:00` window.
@time_machine.travel("20:00:00")
def test_send_today_events_notifications_only_to_individual_bookings_users():
    """
    Test that each stock that is linked to an offer that occurs today and
    creates a job that will send a notification to all of the stock's users
    with a valid (not cancelled) booking, for individual bookings only.
    """
    in_one_hour = date_utils.get_naive_utc_now() + timedelta(hours=1)
    stock_today = offers_factories.EventStockFactory(beginningDatetime=in_one_hour, offer__name="my_offer")

    next_week = date_utils.get_naive_utc_now() + timedelta(days=7)
    stock_next_week = offers_factories.EventStockFactory(beginningDatetime=next_week)

    user1 = users_factories.BeneficiaryGrant18Factory()
    user2 = users_factories.BeneficiaryGrant18Factory()

    # should be fetched
    bookings_factories.BookingFactory(stock=stock_today, user=user1)
    bookings_factories.BookingFactory(stock=stock_today, user=user2)

    # should not be fetched: cancelled
    bookings_factories.BookingFactory(stock=stock_today, status=BookingStatus.CANCELLED, user=user2)

    # should not be fetched: next week
    bookings_factories.BookingFactory(stock=stock_next_week, user=user2)

    send_today_events_notifications_metropolitan_france()

    assert len(testing.requests) == 2
    assert all(data["message"]["title"] == "C'est aujourd'hui !" for data in testing.requests)

    user_ids = {user_id for data in testing.requests for user_id in data["user_ids"]}
    assert user_ids == {user1.id, user2.id}


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(SOON_EXPIRING_BOOKINGS_DAYS_BEFORE_EXPIRATION=3)
def test_notify_users_bookings_not_retrieved() -> None:
    user = users_factories.BeneficiaryGrant18Factory()
    stock = offers_factories.ThingStockFactory()
    creation_date = date_utils.get_naive_utc_now() - constants.BOOKINGS_AUTO_EXPIRY_DELAY + timedelta(days=3)

    # booking that will expire in three days
    booking = bookings_factories.BookingFactory(user=user, stock=stock, dateCreated=creation_date)

    notify_users_bookings_not_retrieved()
    assert len(testing.requests) == 1

    data = testing.requests[0]
    assert data["user_ids"] == [booking.userId]
    assert data["message"]["title"] == "Tu n'as pas récupéré ta réservation"
    assert (
        data["message"]["body"] == f'Vite, il ne te reste plus que 3 jours pour récupérer "{booking.stock.offer.name}"'
    )
