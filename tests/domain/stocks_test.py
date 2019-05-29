import pytest

from domain.stocks import delete_stock_and_cancel_bookings
from tests.test_utils import create_stock, create_booking, create_user


@pytest.mark.standalone
class DeleteStockAndCancelBookingsTest:
    def test_all_booking_are_cancelled(self):
        # given
        user = create_user()
        stock = create_stock()
        stock.bookings = [
            create_booking(user, is_used=True, is_cancelled=False),
            create_booking(user, is_used=True, is_cancelled=False)
        ]

        # when
        bookings = delete_stock_and_cancel_bookings(stock)

        # then
        assert all(map(lambda b: b.isCancelled, bookings))
