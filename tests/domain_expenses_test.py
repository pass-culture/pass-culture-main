from unittest.mock import Mock

import pytest

from domain.expenses import get_expenses
from utils.test_utils import create_booking_for_event, \
    create_booking_for_thing, \
    create_user


@pytest.mark.standalone
class ExpensesTest:
    class MaxTest:
        def test_returns_max_500_and_actual_210(self):
            # Given
            user = create_user()
            booking_1 = create_booking_for_thing(amount=90)
            booking_2 = create_booking_for_event(amount=60, quantity=2)
            booking_3 = create_booking_for_event(amount=20, isCancelled=True)
            find_bookings_by_user_id = Mock(return_value=[booking_1, booking_2, booking_3])

            # When
            expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

            # Then
            assert expenses['all'] == {'max': 500, 'actual': 210}

        def test_returns_max_500_and_actual_0(self):
            # Given
            user = create_user()
            find_bookings_by_user_id = Mock(return_value=[])

            # When
            expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

            # Then
            assert expenses['all'] == {'max': 500, 'actual': 0}

    class PhysicalTest:
        def test_max_200_and_actual_50(self):
            # Given
            user = create_user()
            booking_1 = create_booking_for_thing(amount=50)
            booking_2 = create_booking_for_thing(url='http://test.com', amount=60)

            find_bookings_by_user_id = Mock(return_value=[booking_1, booking_2])

            # When
            expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

            # Then
            assert expenses['physical'] == {'max': 200, 'actual': 50}

        def test_max_200_and_actual_0(self):
            # Given
            user = create_user()
            booking_1 = create_booking_for_thing(url='http://test.com', amount=60)
            find_bookings_by_user_id = Mock(return_value=[booking_1])

            # When
            expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

            # Then
            assert expenses['physical'] == {'max': 200, 'actual': 0}

    class DigitalTest:
        def test_returns_max_200_and_actual_110(self):
            # Given
            user = create_user()
            booking_1 = create_booking_for_thing(amount=50)
            booking_2 = create_booking_for_thing(url='http://test.com', amount=110)

            find_bookings_by_user_id = Mock(return_value=[booking_1, booking_2])

            # When
            expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

            # Then
            assert expenses['digital'] == {'max': 200, 'actual': 110}

        def test_returns_max_200_and_actual_0(self):
            # Given
            user = create_user()
            booking_1 = create_booking_for_thing(amount=50)
            find_bookings_by_user_id = Mock(return_value=[booking_1])

            # When
            expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

            # Then
            assert expenses['digital'] == {'max': 200, 'actual': 0}
