import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.users.api import get_domains_credit
from pcapi.scripts.reimburse_bookings.main import reimburse_booking


@pytest.mark.usefixtures("db_session")
def test_reimbursement():
    booking = BookingFactory.create(quantity=2, status=BookingStatus.REIMBURSED)
    previous_deposit_amount = get_domains_credit(booking.user).all.remaining

    reimburse_booking(booking)

    assert get_domains_credit(booking.user).all.remaining == previous_deposit_amount + booking.total_amount
