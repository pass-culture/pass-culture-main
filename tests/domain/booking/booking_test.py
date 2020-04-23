from domain.booking.booking import Booking


class TotalAmountTest:
    def test_should_return_total_amount(self):
        # Given
        booking = Booking(
            amount=1.2,
            quantity=2,
            is_cancelled=False
        )

        # When
        total_amount = booking.total_amount()

        # Then
        assert total_amount == 2.4
