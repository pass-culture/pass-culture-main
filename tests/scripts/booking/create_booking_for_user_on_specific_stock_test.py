from unittest.mock import MagicMock

from scripts.booking.create_booking_for_user_on_specific_stock import create_booking_for_user_on_specific_stock
from use_cases.book_an_offer import BookingInformation


class CreateBookingForUserOnSpecificStockTest:
    def test_should_call_book_an_offer_use_case_with_expected_parameters(self):
        # Given
        book_an_offer_mock = MagicMock()
        book_an_offer_mock.execute = MagicMock()

        user_id = 12
        stock_id = 15

        # When
        create_booking_for_user_on_specific_stock(
            user_id,
            stock_id,
            book_an_offer_mock,
        )

        # Then
        book_an_offer_mock.execute.assert_called_once()
        use_case_parameters = book_an_offer_mock.execute.call_args[0][0]
        assert isinstance(use_case_parameters, BookingInformation)
        assert use_case_parameters.user_id == user_id
        assert use_case_parameters.stock_id == stock_id
        assert use_case_parameters.quantity == 1
