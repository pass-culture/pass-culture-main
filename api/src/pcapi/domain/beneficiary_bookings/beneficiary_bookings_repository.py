from abc import ABC
from abc import abstractmethod

from pcapi.domain.beneficiary_bookings.beneficiary_bookings_with_stocks import BeneficiaryBookingsWithStocks


class BeneficiaryBookingsRepository(ABC):
    @abstractmethod
    def get_beneficiary_bookings(self, beneficiary_id: int) -> BeneficiaryBookingsWithStocks:
        pass
