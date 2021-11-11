from pcapi.domain.beneficiary_bookings.beneficiary_booking import BeneficiaryBooking
from pcapi.domain.beneficiary_bookings.stock import Stock


class BeneficiaryBookingsWithStocks:
    def __init__(self, bookings: list[BeneficiaryBooking], stocks: list[Stock]):
        self.bookings = bookings
        self.stocks = stocks
