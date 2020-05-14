from domain.booking.booking import Booking
from tests.model_creators.generic_creators import create_user, create_stock


class TotalAmountTest:
    def test_should_return_total_amount(self):
        # Given
        user = create_user()
        stock = create_stock()
        booking = Booking(beneficiary=user, stock=stock, amount=1.2, quantity=2, is_cancelled=False)

        # When
        total_amount = booking.total_amount

        # Then
        assert total_amount == 2.4
