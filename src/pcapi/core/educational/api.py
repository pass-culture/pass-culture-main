from typing import Optional

from pcapi import repository
from pcapi.core.bookings import models as booking_models
from pcapi.core.educational import validation
from pcapi.core.educational.exceptions import EducationalBookingNotFound
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.repository import get_and_lock_educational_deposit


def confirm_educational_booking(educational_booking_id: int) -> booking_models.Booking:
    educational_booking: Optional[EducationalBooking] = (
        EducationalBooking.query.filter(EducationalBooking.id == educational_booking_id)
        .join(booking_models.Booking)
        .one_or_none()
    )
    if educational_booking is None:
        raise EducationalBookingNotFound()

    booking: booking_models.Booking = educational_booking.booking
    if booking.status == booking_models.BookingStatus.CONFIRMED:
        return booking

    educational_institution_id = educational_booking.educationalInstitutionId
    educational_year_id = educational_booking.educationalYearId
    with repository.transaction():
        deposit = get_and_lock_educational_deposit(educational_institution_id, educational_year_id)
        validation.check_institution_fund(
            educational_institution_id,
            educational_year_id,
            booking.total_amount,
            deposit,
        )
        booking.mark_as_confirmed()
        repository.repository.save(booking)
        return booking
