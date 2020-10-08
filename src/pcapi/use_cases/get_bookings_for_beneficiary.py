from pcapi.domain.beneficiary_bookings.beneficiary_bookings_with_stocks import BeneficiaryBookingsWithStocks
from pcapi.domain.beneficiary_bookings.beneficiary_bookings_repository import BeneficiaryBookingsRepository


class GetBookingsForBeneficiary:
    def __init__(self, beneficiary_bookings_repository: BeneficiaryBookingsRepository):
        self.beneficiary_bookings_repository = beneficiary_bookings_repository

    def execute(self, beneficiary_id: int) -> BeneficiaryBookingsWithStocks:
        return self.beneficiary_bookings_repository.get_beneficiary_bookings(
            beneficiary_id=beneficiary_id
        )
