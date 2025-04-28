import datetime

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import utils as educational_utils


def update_collective_stock_booking(
    stock: educational_models.CollectiveStock,
    current_booking: educational_models.CollectiveBooking | None,
    start_datetime_has_changed: bool,
) -> None:
    """When a collective stock is updated, we also update some fields of its related booking"""

    # if the booking limit date is set in the future and a PENDING booking was automatically cancelled, set it back to PENDING
    last_booking = stock.lastBooking
    booking_limit_value = stock.bookingLimitDatetime
    expired_booking_to_update = None
    if _should_update_collective_booking_pending(last_booking, booking_limit_value):
        assert last_booking is not None  # checked by should_update_collective_booking_pending
        expired_booking_to_update = last_booking
        _update_collective_booking_pending(last_booking)

    # the booking to update should either be the expired booking that was set back to PENDING
    # or the non-cancelled booking (there should not be one of each at the same time)
    if expired_booking_to_update and current_booking:
        raise educational_exceptions.MultipleCollectiveBookingFound()

    booking_to_update = expired_booking_to_update or current_booking
    if booking_to_update:
        booking_to_update.confirmationLimitDate = booking_limit_value

        if start_datetime_has_changed:
            _update_collective_booking_cancellation_limit_date(booking_to_update, stock.startDatetime)
            _update_collective_booking_educational_year_id(booking_to_update, stock.startDatetime)


def _update_collective_booking_educational_year_id(
    booking: educational_models.CollectiveBooking,
    new_start_datetime: datetime.datetime,
) -> None:
    educational_year = educational_repository.find_educational_year_by_date(new_start_datetime)
    if educational_year is None:
        raise educational_exceptions.EducationalYearNotFound()

    booking.educationalYear = educational_year


def _update_collective_booking_cancellation_limit_date(
    booking: educational_models.CollectiveBooking, new_start_datetime: datetime.datetime
) -> None:
    # if the input date has a timezone (resp. does not have one), we need to compare it with an aware datetime (resp. a naive datetime)
    now = (
        datetime.datetime.utcnow()
        if new_start_datetime.tzinfo is None
        else datetime.datetime.now(datetime.timezone.utc)
    )
    booking.cancellationLimitDate = educational_utils.compute_educational_booking_cancellation_limit_date(
        new_start_datetime, now
    )


def _update_collective_booking_pending(expired_booking: educational_models.CollectiveBooking) -> None:
    expired_booking.status = educational_models.CollectiveBookingStatus.PENDING
    expired_booking.cancellationReason = None
    expired_booking.cancellationDate = None


def _should_update_collective_booking_pending(
    booking: educational_models.CollectiveBooking | None, booking_limit: datetime.datetime
) -> bool:
    return booking is not None and booking.is_expired and booking_limit > datetime.datetime.utcnow()
