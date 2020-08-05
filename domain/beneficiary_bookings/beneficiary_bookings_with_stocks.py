from typing import List

from domain.beneficiary_bookings.beneficiary_booking import BeneficiaryBooking
from domain.beneficiary_bookings.stock import Stock


class BeneficiaryBookingsWithStocks:
    def __init__(self, bookings: List[BeneficiaryBooking], stocks: List[Stock]):
        self.bookings = bookings
        self.stocks = stocks
