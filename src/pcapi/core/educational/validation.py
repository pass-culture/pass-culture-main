from decimal import Decimal

from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.repository import get_confirmed_educational_bookings_amount


def check_institution_fund(
    educational_institution_id: int,
    educational_year_id: str,
    booking_amount: Decimal,
    deposit: EducationalDeposit,
) -> None:
    spent_amount = get_confirmed_educational_bookings_amount(educational_institution_id, educational_year_id)
    total_amount = booking_amount + spent_amount

    deposit.check_has_enough_fund(total_amount)
