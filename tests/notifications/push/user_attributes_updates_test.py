from datetime import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.testing import assert_num_queries
from pcapi.core.users.factories import UserFactory
from pcapi.notifications.push.user_attributes_updates import BATCH_DATETIME_FORMAT
from pcapi.notifications.push.user_attributes_updates import get_user_booking_attributes


pytestmark = pytest.mark.usefixtures("db_session")


class GetUserBookingAttributesTest:
    def test_get_attributes(self):
        user = UserFactory()
        b1 = BookingFactory(user=user, amount=10)
        b2 = BookingFactory(user=user, amount=10, dateUsed=datetime(2021, 5, 6))
        b3 = BookingFactory(user=user, amount=10, dateUsed=datetime(2021, 7, 8))
        BookingFactory(user=user, amount=100, isCancelled=True)

        n_query_get_user = 1
        n_query_get_bookings = 1
        n_query_get_deposit = 1

        with assert_num_queries(n_query_get_user + n_query_get_bookings + n_query_get_deposit):
            attributes = get_user_booking_attributes(user)

        last_date_created = max(booking.dateCreated for booking in [b1, b2, b3])

        assert attributes == {
            f"date(u.booked_product_{b2.stock.offer.product.id}_date_used)": b2.dateUsed.strftime(
                BATCH_DATETIME_FORMAT
            ),
            f"date(u.booked_product_{b3.stock.offer.product.id}_date_used)": b3.dateUsed.strftime(
                BATCH_DATETIME_FORMAT
            ),
            "date(u.last_booking_date)": last_date_created.strftime(BATCH_DATETIME_FORMAT),
            "u.credit": 47000,
            "ut.booking_categories": ["ThingType.AUDIOVISUEL"],
        }

    def test_get_attributes_without_bookings(self):
        user = UserFactory()

        n_query_get_user = 1
        n_query_get_bookings = 1
        n_query_get_deposit = 1

        with assert_num_queries(n_query_get_user + n_query_get_bookings + n_query_get_deposit):
            attributes = get_user_booking_attributes(user)

        assert attributes == {
            "date(u.last_booking_date)": None,
            "u.credit": 50000,
        }
