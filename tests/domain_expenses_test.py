from unittest.mock import Mock

import pytest

from domain.expenses import get_expenses
from models import Booking
from utils.test_utils import create_user


@pytest.mark.standalone
def test_get_expenses_should_have_max_500_and_actual_150_at_key_all_when_sum_bookings_amount_150():
    # Given
    user = create_user()
    booking_1 = Booking(from_dict={'amount': 90})
    booking_2 = Booking(from_dict={'amount': 60})
    find_bookings_by_user_id = Mock(return_value=[booking_1, booking_2])

    # When
    expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

    # Then
    assert expenses['all'] == {'max': 500, 'actual': 150}

# @pytest.mark.standalone
# @clean_database
# def test_get_expenses_should_have_max_200_and_actual_50_at_key_digital_when_sum_amount_bookings_filtered_by_stock_digital_50(app):
#     # Given
#     user = create_user()
#     user.save()
#
#     offerer = create_offerer()
#     offerer.save()
#
#     venue = create_venue(offerer)
#     venue.save()
#
#     thing_offer = create_thing_offer(venue)
#     thing_offer.save()
#
#     stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=50)
#     stock.save()
#
#     deposit = create_deposit(user, date=datetime.utcnow() - timedelta(minutes=2), amount=500)
#     deposit.save()
#
#     booking = create_booking(user, stock, recommendation=None)
#     booking.save()
#
#
#     # When
#     expenses = get_expenses(user)
#
#     # Then
#     assert expenses['all'] == {'max': 500, 'actual': 150}
