from unittest.mock import patch

import pytest

from domain.users import UnauthorizedForAdminUser
from tests.domain_creators.generic_creators import create_domain_thing_booking_recap, create_domain_event_booking_recap
from model_creators.generic_creators import create_user
from use_cases.get_all_bookings_by_pro_user import get_all_bookings_by_pro_user


class GetAllBookingsByProUserTest:
    @patch('use_cases.get_all_bookings_by_pro_user.check_is_authorized_to_access_bookings_recap')
    @patch('use_cases.get_all_bookings_by_pro_user.user_queries.find_user_by_id')
    @patch('use_cases.get_all_bookings_by_pro_user.booking_queries.find_by_pro_user_id')
    def test_should_retrieve_all_user_bookings(self,
                                               find_by_pro_user_id,
                                               find_user_by_id,
                                               check_is_authorized_to_access_bookings_recap):
        # Given
        user = create_user(is_admin=False, can_book_free_offers=True)

        booking = create_domain_thing_booking_recap()
        booking2 = create_domain_event_booking_recap()

        find_user_by_id.return_value = user
        find_by_pro_user_id.return_value = [booking, booking2]

        # When
        bookings = get_all_bookings_by_pro_user(user.id)

        # Then
        find_user_by_id.assert_called_once_with(user.id)
        check_is_authorized_to_access_bookings_recap.assert_called_once_with(user)
        find_by_pro_user_id.assert_called_once_with(user_id=user.id, page=0)
        assert bookings == [booking, booking2]

    @patch('use_cases.get_all_bookings_by_pro_user.user_queries.find_user_by_id')
    @patch('use_cases.get_all_bookings_by_pro_user.check_is_authorized_to_access_bookings_recap')
    @patch('use_cases.get_all_bookings_by_pro_user.booking_queries.find_by_pro_user_id')
    def test_should_not_retrieve_bookings_when_user_is_not_authorized(self,
                                                                      find_by_pro_user_id,
                                                                      check_is_authorized_to_access_bookings_recap,
                                                                      find_user_by_id):
        # Given
        user = create_user()
        check_is_authorized_to_access_bookings_recap.side_effect = UnauthorizedForAdminUser()

        # When
        with pytest.raises(UnauthorizedForAdminUser):
            get_all_bookings_by_pro_user(user.id)

        # Then
        find_by_pro_user_id.assert_not_called()
