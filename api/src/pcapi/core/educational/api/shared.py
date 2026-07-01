import datetime
import decimal
import typing

from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational import utils
from pcapi.models import db
from pcapi.utils import date as date_utils


def update_collective_stock_booking(
    stock: models.CollectiveStock,
    current_booking: models.CollectiveBooking | None,
    start_datetime_has_changed: bool,
) -> None:
    """When a collective stock is updated, we also update some fields of its related booking"""

    # if the booking limit date is set in the future and a PENDING booking was automatically cancelled, set it back to PENDING
    last_booking = stock.lastBooking
    booking_limit_value = stock.bookingLimitDatetime
    expired_booking_to_update = None
    if last_booking is not None and _should_update_collective_booking_pending(last_booking, booking_limit_value):
        expired_booking_to_update = last_booking
        _update_collective_booking_pending(last_booking)

    # the booking to update should either be the expired booking that was set back to PENDING
    # or the non-cancelled booking (there should not be one of each at the same time)
    if expired_booking_to_update and current_booking:
        raise exceptions.MultipleCollectiveBookingFound()

    booking_to_update = expired_booking_to_update or current_booking
    if booking_to_update:
        booking_to_update.confirmationLimitDate = booking_limit_value

        if start_datetime_has_changed:
            _update_collective_booking_cancellation_limit_date(booking_to_update, stock.startDatetime)
            _update_collective_booking_educational_year_id(booking_to_update, stock.startDatetime)


def _update_collective_booking_educational_year_id(
    booking: models.CollectiveBooking, new_start_datetime: datetime.datetime
) -> None:
    educational_year = repository.find_educational_year_by_date(new_start_datetime)
    if educational_year is None:
        raise exceptions.EducationalYearNotFound()

    booking.educationalYear = educational_year


def _update_collective_booking_cancellation_limit_date(
    booking: models.CollectiveBooking, new_start_datetime: datetime.datetime
) -> None:
    now = date_utils.get_naive_utc_now()
    new_start = date_utils.to_naive_utc_datetime(new_start_datetime)

    booking.cancellationLimitDate = utils.compute_educational_booking_cancellation_limit_date(new_start, now)


def _update_collective_booking_pending(expired_booking: models.CollectiveBooking) -> None:
    expired_booking.status = models.CollectiveBookingStatus.PENDING
    expired_booking.cancellationReason = None
    expired_booking.cancellationDate = None


def _should_update_collective_booking_pending(
    booking: models.CollectiveBooking, booking_limit: datetime.datetime
) -> bool:
    now = date_utils.get_naive_utc_now()
    limit = date_utils.to_naive_utc_datetime(booking_limit)

    return booking.is_expired and limit > now


class AdditionalFeeDict(typing.TypedDict):
    type: models.CollectiveAdditionalFeeType
    label: typing.NotRequired[str | None]
    amount: decimal.Decimal


def update_additional_fees(
    new_additional_fees: list[AdditionalFeeDict], collective_stock: models.CollectiveStock
) -> None:
    new_amount_by_type_label = {(fee["type"], fee.get("label")): fee["amount"] for fee in new_additional_fees}
    current_fee_by_type_label = {(fee.type, fee.label): fee for fee in collective_stock.collectiveAdditionalFees}

    for type_label, new_amount in new_amount_by_type_label.items():
        # type / label found -> update the row
        if type_label in current_fee_by_type_label:
            current_fee_by_type_label[type_label].amount = new_amount
        # type / label not found -> add a row
        else:
            fee_type, fee_label = type_label
            db.session.add(
                models.CollectiveAdditionalFee(
                    type=fee_type, label=fee_label, amount=new_amount, collectiveStock=collective_stock
                )
            )

    # remove current type / label rows that are not present in the input
    to_delete = [
        fee.id
        for fee in collective_stock.collectiveAdditionalFees
        if (fee.type, fee.label) not in new_amount_by_type_label
    ]
    if to_delete:
        db.session.query(models.CollectiveAdditionalFee).filter(
            models.CollectiveAdditionalFee.id.in_(to_delete)
        ).delete()

    db.session.flush()
