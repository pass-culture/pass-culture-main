from unittest.mock import MagicMock

from pcapi.infrastructure.repository.beneficiary_bookings.beneficiary_bookings_sql_repository import \
    BeneficiaryBookingsSQLRepository
from pcapi.use_cases.get_bookings_for_beneficiary import GetBookingsForBeneficiary


class GetBookingsForBeneficiaryTest:
    def setup_method(self):
        self.beneficiary_bookings_repository = BeneficiaryBookingsSQLRepository()
        self.beneficiary_bookings_repository.get_beneficiary_bookings = MagicMock()
        self.get_bookings_for_beneficiary = GetBookingsForBeneficiary(
            beneficiary_bookings_repository=self.beneficiary_bookings_repository
        )

    def should_call_get_beneficiary_bookings(self):
        # Given
        beneficiary_id = 12

        # When
        self.get_bookings_for_beneficiary.execute(beneficiary_id=beneficiary_id)

        # Then
        self.beneficiary_bookings_repository.get_beneficiary_bookings.assert_called_once_with(
            beneficiary_id=beneficiary_id
        )
