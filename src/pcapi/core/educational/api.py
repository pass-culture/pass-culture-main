from pcapi import repository
from pcapi.core.bookings import models as booking_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation
from pcapi.core.educational.exceptions import EducationalBookingNotFound


def confirm_educational_booking(educational_booking_id: int) -> booking_models.Booking:
    educational_booking = educational_repository.find_educational_booking_by_id(educational_booking_id)
    if educational_booking is None:
        raise EducationalBookingNotFound()

    booking: booking_models.Booking = educational_booking.booking
    if booking.status == booking_models.BookingStatus.CONFIRMED:
        return booking

    educational_institution_id = educational_booking.educationalInstitutionId
    educational_year_id = educational_booking.educationalYearId
    with repository.transaction():
        deposit = educational_repository.get_and_lock_educational_deposit(
            educational_institution_id, educational_year_id
        )
        validation.check_institution_fund(
            educational_institution_id,
            educational_year_id,
            booking.total_amount,
            deposit,
        )
        booking.mark_as_confirmed()
        repository.repository.save(booking)
        return booking
