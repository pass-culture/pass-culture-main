from decimal import Decimal
from operator import and_
from typing import Optional

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.exceptions import EducationalDepositNotFound
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalDeposit


def get_and_lock_educational_deposit(educational_institution_id: int, educational_year_id: str) -> EducationalDeposit:
    """Returns educational_deposit with a FOR UPDATE lock
    Raises EducationalDepositNotFound if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    educational_deposit = (
        EducationalDeposit.query.filter_by(
            educationalInstitutionId=educational_institution_id,
            educationalYearId=educational_year_id,
        )
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not educational_deposit:
        raise EducationalDepositNotFound()
    return educational_deposit


def get_confirmed_educational_bookings_amount(
    educational_institution_id: int,
    educational_year_id: str,
) -> Decimal:
    educational_bookings = (
        EducationalBooking.query.filter_by(
            educationalInstitutionId=educational_institution_id, educationalYearId=educational_year_id
        )
        .join(Booking)
        .filter(and_(Booking.isCancelled.is_(False), Booking.status != BookingStatus.PENDING))
        .options(joinedload(EducationalBooking.booking).load_only(Booking.amount, Booking.quantity))
        .all()
    )
    return Decimal(sum([educational_booking.booking.total_amount for educational_booking in educational_bookings]))


def find_educational_booking_by_id(educational_booking_id: int) -> Optional[EducationalBooking]:
    return EducationalBooking.query.filter(EducationalBooking.id == educational_booking_id).join(Booking).one_or_none()
