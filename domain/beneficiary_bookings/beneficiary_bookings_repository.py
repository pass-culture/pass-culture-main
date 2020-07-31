from abc import ABC, abstractmethod

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBookings


class BeneficiaryBookingsRepository(ABC):
    @abstractmethod
    def get_beneficiary_bookings(self, beneficiary_id: int) -> BeneficiaryBookings:
        pass
