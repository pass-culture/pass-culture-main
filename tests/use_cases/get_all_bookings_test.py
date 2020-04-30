from datetime import datetime
from unittest.mock import patch

import pytest

from domain.booking_recap.booking_recap import BookingRecap, BookingRecapStatus
from domain.users import UnauthorizedForAdminUser
from tests.model_creators.generic_creators import create_user
from use_cases.get_all_bookings_by_pro_user import get_all_bookings_by_pro_user


class BookingRecapMock(BookingRecap):
    def __init__(self):
        super().__init__(
            offer_name="Nom de mon offre",
            beneficiary_lastname="Polastri",
            beneficiary_firstname="Eve",
            beneficiary_email="eve.polastri@example.com",
            booking_token="ABCDE",
            booking_date=datetime.utcnow(),
            booking_status=BookingRecapStatus.validated,
        )


class GetAllBookingsTest:
    @patch('use_cases.get_all_bookings_by_pro_user.check_is_authorized_to_access_bookings_recap')
    @patch('use_cases.get_all_bookings_by_pro_user.user_queries.find_user_by_id')
    @patch('use_cases.get_all_bookings_by_pro_user.booking_queries.find_by_pro_user_id')
    def test_should_retrieve_all_user_bookings(self, find_by_pro_user_id, find_user_by_id,
                                               check_is_authorized_to_access_bookings_recap):
        # Given
        user = create_user(is_admin=False, can_book_free_offers=True)

        booking = BookingRecapMock()
        booking2 = BookingRecapMock()

        find_user_by_id.return_value = user
        find_by_pro_user_id.return_value = [booking, booking2]

        # When
        bookings = get_all_bookings_by_pro_user(user.id)

        # Then
        find_user_by_id.assert_called_once_with(user.id)
        check_is_authorized_to_access_bookings_recap.assert_called_once_with(user)
        find_by_pro_user_id.assert_called_once_with(user.id)
        assert bookings == [booking, booking2]

    @patch('use_cases.get_all_bookings_by_pro_user.user_queries.find_user_by_id')
    @patch('use_cases.get_all_bookings_by_pro_user.check_is_authorized_to_access_bookings_recap')
    @patch('use_cases.get_all_bookings_by_pro_user.booking_queries.find_by_pro_user_id')
    def test_should_not_retrieve_bookings_when_user_is_not_authorized(self, find_by_pro_user_id,
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
