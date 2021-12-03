from pcapi.infrastructure.repository.beneficiary_bookings.beneficiary_bookings_sql_repository import (
    BeneficiaryBookingsSQLRepository,
)
from pcapi.use_cases.get_bookings_for_beneficiary import GetBookingsForBeneficiary


beneficiary_bookings_repository = BeneficiaryBookingsSQLRepository()

# Usecases
get_bookings_for_beneficiary = GetBookingsForBeneficiary(
    beneficiary_bookings_repository=beneficiary_bookings_repository
)
