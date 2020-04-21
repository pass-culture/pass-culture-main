from unittest.mock import patch

import pytest

from domain.users import UnauthorizedForAdminUser
from models import Booking
from tests.model_creators.generic_creators import create_user
from use_cases.get_all_bookings_by_pro_user import get_all_bookings_by_pro_user


class GetAllBookingsTest:
    @patch('use_cases.get_all_bookings_by_pro_user.check_user_is_not_admin')
    @patch('use_cases.get_all_bookings_by_pro_user.user_queries.find_user_by_id')
    @patch('use_cases.get_all_bookings_by_pro_user.booking_queries.find_by_pro_user_id')
    def test_should_retrieve_all_user_bookings(self, find_by_pro_user_id, find_user_by_id, check_user_is_not_admin):
        # Given
        user = create_user(is_admin=False, can_book_free_offers=True)
        booking = Booking()
        booking2 = Booking()

        find_user_by_id.return_value = user
        find_by_pro_user_id.return_value = [booking, booking2]

        # When
        bookings = get_all_bookings_by_pro_user(user.id)

        # Then
        find_user_by_id.assert_called_once_with(user.id)
        check_user_is_not_admin.assert_called_once_with(user)
        find_by_pro_user_id.assert_called_once_with(user.id)
        assert bookings == [booking, booking2]

    @patch('use_cases.get_all_bookings_by_pro_user.user_queries.find_user_by_id')
    def test_should_raise_exception_when_user_is_admin(self, find_user_by_id):
        # Given
        user = create_user(is_admin=True, can_book_free_offers=False)
        find_user_by_id.return_value = user

        # When
        with pytest.raises(UnauthorizedForAdminUser) as exception:
            get_all_bookings_by_pro_user(user.id)

        # Then
        assert exception.value.errors['global'] == [
            "Le statut d'administrateur ne permet pas d'accéder au suivi des réservations"]
