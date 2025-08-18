import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.finance.models import RecreditType
from pcapi.scripts.reimburse_bookings.main import BOOKING_TO_REIMBURSE_TOKENS
from pcapi.scripts.reimburse_bookings.main import reimburse_bookings


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize("token", BOOKING_TO_REIMBURSE_TOKENS)
@pytest.mark.parametrize("quantity", [1, 2])
def test_reimburse_bookings(token, quantity):
    booking = BookingFactory(status=BookingStatus.CANCELLED, token=token, quantity=quantity)
    deposit = booking.user.deposit
    old_deposit_amount = deposit.amount

    reimburse_bookings(not_dry=True)

    expected_recredited_amount = quantity * booking.stock.price
    new_deposit_amount = deposit.amount
    assert new_deposit_amount == old_deposit_amount + expected_recredited_amount

    latest_recredit = max(deposit.recredits, key=lambda recredit: recredit.id)
    assert latest_recredit.amount == expected_recredited_amount
    assert latest_recredit.recreditType == RecreditType.MANUAL_MODIFICATION
