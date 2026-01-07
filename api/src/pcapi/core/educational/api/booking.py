import datetime
import decimal
import logging
from functools import partial

import sqlalchemy.orm as sa_orm
from pydantic.v1.error_wrappers import ValidationError

from pcapi import settings
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational import schemas
from pcapi.core.educational import utils
from pcapi.core.educational import validation
from pcapi.core.educational.serialization import collective_booking as collective_booking_serialize
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import repository as finance_repository
from pcapi.core.mails import transactional as transactional_mails
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)


def book_collective_offer(
    redactor_informations: schemas.RedactorInformation, stock_id: int
) -> models.CollectiveBooking:
    redactor = repository.find_or_create_redactor(redactor_informations)

    educational_institution = repository.find_educational_institution_by_uai_code(redactor_informations.uai)
    if not educational_institution:
        raise exceptions.EducationalInstitutionUnknown()

    stock = repository.get_and_lock_collective_stock(stock_id=stock_id)
    validation.check_collective_stock_is_bookable(stock)

    educational_year = repository.find_educational_year_by_date(stock.startDatetime)
    if not educational_year:
        raise exceptions.EducationalYearNotFound()
    validation.check_user_can_prebook_collective_stock(redactor_informations.uai, stock)

    utcnow = date_utils.get_naive_utc_now()
    booking = models.CollectiveBooking(
        educationalInstitution=educational_institution,
        educationalYear=educational_year,
        educationalRedactor=redactor,
        confirmationLimitDate=stock.bookingLimitDatetime,
        collectiveStockId=stock.id,
        venueId=stock.collectiveOffer.venueId,
        offererId=stock.collectiveOffer.venue.managingOffererId,
        status=models.CollectiveBookingStatus.PENDING,
        dateCreated=utcnow,
        cancellationLimitDate=utils.compute_educational_booking_cancellation_limit_date(stock.startDatetime, utcnow),
    )
    db.session.add(booking)
    db.session.flush()

    # re-fetch the booking to load the relations used during seralization
    new_booking = repository.find_collective_booking_by_id(booking_id=booking.id)
    assert new_booking is not None

    logger.info(
        "Redactor booked a collective offer",
        extra={
            "redactor": redactor_informations.email,
            "offerId": stock.collectiveOfferId,
            "stockId": stock.id,
            "bookingId": new_booking.id,
        },
    )

    transactional_mails.send_eac_new_collective_prebooking_email_to_pro(new_booking)

    on_commit(partial(_notify_prebooking, data=collective_booking_serialize.serialize_collective_booking(new_booking)))

    return new_booking


def _notify_prebooking(data: schemas.EducationalBookingResponse) -> None:
    try:
        adage_client.notify_prebooking(data=data)
    except exceptions.AdageException as adage_error:
        logger.error(
            "%s Educational institution will not receive a confirmation email.",
            adage_error.message,
            extra={
                "bookingId": data.id,
                "adage status code": adage_error.status_code,
                "adage response text": adage_error.response_text,
            },
        )
    except ValidationError:
        logger.exception(
            "Could not notify adage of prebooking, hence send confirmation email to educational institution, as educationalBooking serialization failed.",
            extra={"bookingId": data.id},
        )


def confirm_collective_booking(educational_booking_id: int) -> models.CollectiveBooking:
    collective_booking = repository.find_collective_booking_by_id(educational_booking_id)

    if collective_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if collective_booking.status == models.CollectiveBookingStatus.CONFIRMED:
        return collective_booking

    utils.log_information_for_data_purpose(
        event_name="BookingApproval",
        extra_data={
            "stockId": collective_booking.collectiveStockId,
            "bookingId": educational_booking_id,
        },
        uai=None,
        user_role=None,
    )

    validation.check_collective_booking_status(collective_booking)

    confirmation_datetime = date_utils.get_naive_utc_now()
    validation.check_confirmation_limit_date_has_not_passed(collective_booking, confirmation_datetime)

    # TODO(jcicurel-pass, 2026-01-07): we must block confirmation for Agriculture UAIs
    # remove this once we have updated the Agriculture deposits
    deposit = (
        db.session.query(models.EducationalDeposit)
        .filter(
            models.EducationalDeposit.educationalInstitutionId == collective_booking.educationalInstitutionId,
            models.EducationalDeposit.period.op("@>")(confirmation_datetime),  # current deposit
        )
        .one_or_none()
    )
    if deposit is not None and deposit.ministry == models.Ministry.AGRICULTURE:
        raise exceptions.InsufficientFund()

    if settings.EAC_CHECK_INSTITUTION_FUND:
        _check_institution_fund_and_link_deposit(collective_booking, confirmation_datetime)

    collective_booking.mark_as_confirmed(confirmation_datetime)

    db.session.add(collective_booking)
    db.session.flush()

    logger.info(
        "Head of institution confirmed an educational offer",
        extra={"collectiveBookingId": collective_booking.id},
    )

    transactional_mails.send_eac_new_booking_email_to_pro(collective_booking)

    return collective_booking


def _check_institution_fund_and_link_deposit(
    collective_booking: models.CollectiveBooking, confirmation_datetime: datetime.datetime
) -> None:
    deposit = repository.get_and_lock_educational_deposit(
        educational_institution_id=collective_booking.educationalInstitutionId,
        educational_year=collective_booking.educationalYear,
        confirmation_datetime=confirmation_datetime,
    )

    validation.check_institution_fund(booking_amount=collective_booking.collectiveStock.price, deposit=deposit)

    # link the booking to the deposit so that we can easily get all confirmed bookings from a given deposit
    # e.g in the institution fund check above
    collective_booking.educationalDeposit = deposit


def refuse_collective_booking(educational_booking_id: int) -> models.CollectiveBooking:
    collective_booking = repository.find_collective_booking_by_id(educational_booking_id)
    if collective_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if collective_booking.status == models.CollectiveBookingStatus.CANCELLED:
        return collective_booking

    try:
        collective_booking.mark_as_refused()
    except (
        exceptions.EducationalBookingNotRefusable,
        exceptions.CollectiveBookingAlreadyCancelled,
    ) as exception:
        logger.info(
            "User from adage trying to refuse collective booking that cannot be refused",
            extra={
                "collective_booking_id": collective_booking.id,
                "exception_type": exception.__class__.__name__,
            },
        )
        raise exception

    db.session.add(collective_booking)
    db.session.flush()

    logger.info(
        "Collective Booking has been cancelled",
        extra={
            "booking": collective_booking.id,
            "reason": str(collective_booking.cancellationReason),
        },
    )

    transactional_mails.send_eac_booking_cancellation_email(collective_booking)

    return collective_booking


def cancel_collective_offer_booking(offer_id: int, author_id: int, user_connect_as: bool) -> None:
    collective_offer: models.CollectiveOffer | None = (
        db.session.query(models.CollectiveOffer)
        .filter(models.CollectiveOffer.id == offer_id)
        .options(
            sa_orm.joinedload(models.CollectiveOffer.collectiveStock).joinedload(
                models.CollectiveStock.collectiveBookings
            )
        )
        .first()
    )

    if collective_offer is None:
        raise exceptions.CollectiveOfferNotFound()

    validation.check_collective_offer_action_is_allowed(
        collective_offer, models.CollectiveOfferAllowedAction.CAN_CANCEL
    )

    if collective_offer.collectiveStock is None:
        raise exceptions.CollectiveStockNotFound()

    collective_stock = collective_offer.collectiveStock
    cancelled_booking = _cancel_collective_booking_by_offerer(collective_stock, author_id, user_connect_as)

    logger.info(
        "Cancelled collective booking from offer",
        extra={"collective_stock": collective_stock.id, "collective_booking": cancelled_booking.id},
    )

    on_commit(
        partial(
            notify_redactor_that_booking_has_been_cancelled,
            collective_booking_serialize.serialize_collective_booking(cancelled_booking),
        ),
    )
    notify_pro_that_booking_has_been_cancelled(cancelled_booking)


def notify_pro_users_one_day_before() -> None:
    bookings = repository.find_bookings_starting_in_x_days(1)
    for booking in bookings:
        transactional_mails.send_eac_alert_one_day_before_event(booking)


def notify_pro_users_one_day_after() -> None:
    bookings = repository.find_bookings_ending_in_x_days(-1)
    for booking in bookings:
        transactional_mails.send_eac_alert_one_day_after_event(booking)


def notify_pro_pending_booking_confirmation_limit_in_3_days() -> None:
    bookings = repository.find_pending_booking_confirmation_limit_date_in_3_days()
    for booking in bookings:
        transactional_mails.send_eac_pending_booking_confirmation_limit_date_in_3_days(booking)


def _cancel_collective_booking(
    collective_booking: models.CollectiveBooking,
    reason: models.CollectiveBookingCancellationReasons,
    author_id: int,
) -> None:
    repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
    db.session.refresh(collective_booking)

    try:
        # The booking cannot be used nor reimbursed yet, otherwise
        # `cancel_booking` will fail. Thus, there is no finance
        # event to cancel here.
        collective_booking.cancel_booking(reason, author_id=author_id)
    except exceptions.CollectiveBookingAlreadyCancelled:
        mark_transaction_as_invalid()
        return

    db.session.flush()

    logger.info(
        "CollectiveBooking has been cancelled",
        extra={
            "collective_booking": collective_booking.id,
            "reason": str(reason),
        },
    )


def _cancel_collective_booking_by_offerer(
    collective_stock: models.CollectiveStock, author_id: int, user_connect_as: bool
) -> models.CollectiveBooking:
    booking_to_cancel: models.CollectiveBooking | None = next(
        (
            collective_booking
            for collective_booking in collective_stock.collectiveBookings
            if collective_booking.is_cancellable_from_offerer
        ),
        None,
    )

    if booking_to_cancel is None:
        raise exceptions.NoCollectiveBookingToCancel()

    if user_connect_as:
        cancellation_reason = models.CollectiveBookingCancellationReasons.OFFERER_CONNECT_AS
    else:
        cancellation_reason = models.CollectiveBookingCancellationReasons.OFFERER

    _cancel_collective_booking(booking_to_cancel, cancellation_reason, author_id)

    return booking_to_cancel


def cancel_collective_booking(
    collective_booking: models.CollectiveBooking,
    reason: models.CollectiveBookingCancellationReasons,
    force: bool = True,
    _from: str | None = None,
    author_id: int | None = None,
) -> None:
    collective_booking_id = collective_booking.id
    with atomic():
        repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
        db.session.refresh(collective_booking)

        if finance_repository.has_reimbursement(collective_booking):
            raise exceptions.BookingIsAlreadyRefunded()

        cancelled_event = finance_api.cancel_latest_event(collective_booking)

        collective_booking.cancel_booking(reason=reason, cancel_even_if_used=force, author_id=author_id)
        db.session.flush()

        if cancelled_event:
            finance_api.add_event(
                finance_models.FinanceEventMotive.BOOKING_CANCELLED_AFTER_USE,
                booking=collective_booking,
            )

    logger.info(
        "CollectiveBooking has been cancelled by %s %s",
        reason.value.lower(),
        f"from {_from}" if _from else "",
        extra={"collective_booking": collective_booking_id, "reason": reason.value},
    )


def uncancel_collective_booking(collective_booking: models.CollectiveBooking) -> None:
    repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
    db.session.refresh(collective_booking)
    collective_booking.uncancel_booking()
    if collective_booking.status == models.CollectiveBookingStatus.USED:
        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
            booking=collective_booking,
        )
    db.session.flush()

    logger.info(
        "CollectiveBooking has been uncancelled by support",
        extra={
            "collective_booking": collective_booking.id,
            "new_status": collective_booking.status,
        },
    )


def notify_reimburse_collective_booking(
    collective_booking: models.CollectiveBooking,
    reason: str,
    value: decimal.Decimal | None = None,
    details: str = "",
) -> None:
    price = collective_booking.collectiveStock.price
    value = value or price
    if value > price:
        raise ValueError(
            f"Collective booking {collective_booking.id} is priced at {price}. We cannot reimburse more than that."
        )
    on_commit(
        partial(
            adage_client.notify_reimburse_collective_booking,
            data=collective_booking_serialize.serialize_reimbursement_notification(
                collective_booking=collective_booking,
                reason=reason,
                value=value,
                details=details,
            ),
        ),
    )


def update_collective_bookings_for_new_institution(
    booking_ids: list[int],
    institution_source: models.EducationalInstitution,
    institution_destination: models.EducationalInstitution,
) -> None:
    offer_ids = (
        db.session.query(models.CollectiveOffer)
        .join(models.CollectiveStock)
        .join(models.CollectiveBooking)
        .filter(
            models.CollectiveBooking.id.in_(booking_ids),
            models.CollectiveBooking.educationalInstitutionId == institution_source.id,
        )
        .with_entities(models.CollectiveOffer.id)
    )

    db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id.in_(offer_ids)).update(
        {"institutionId": institution_destination.id}, synchronize_session=False
    )

    db.session.query(models.CollectiveBooking).filter(
        models.CollectiveBooking.id.in_(booking_ids),
        models.CollectiveBooking.educationalInstitutionId == institution_source.id,
    ).update({"educationalInstitutionId": institution_destination.id}, synchronize_session=False)

    db.session.flush()


def notify_redactor_that_booking_has_been_cancelled(booking: schemas.EducationalBookingResponse) -> None:
    try:
        adage_client.notify_booking_cancellation_by_offerer(data=booking)
    except exceptions.AdageException as adage_error:
        logger.error(
            "%s Could not notify adage of collective booking cancellation by offerer. Educational institution won't be notified.",
            adage_error.message,
            extra={
                "collectiveBookingId": booking.id,
                "adage status code": adage_error.status_code,
                "adage response text": adage_error.response_text,
            },
        )
    except ValidationError:
        logger.exception(
            "Could not notify adage of prebooking, hence send booking cancellation email to educational institution, as educationalBooking serialization failed.",
            extra={
                "collectiveBookingId": booking.id,
            },
        )


def notify_pro_that_booking_has_been_cancelled(booking: models.CollectiveBooking) -> None:
    transactional_mails.send_collective_booking_cancellation_confirmation_by_pro_email(booking)


def handle_expired_collective_bookings() -> None:
    logger.info("[handle_expired_collective_bookings] Start")

    try:
        _cancel_expired_collective_bookings()
    except Exception as e:
        logger.exception("Error in cancel_expired_collective_bookings : %s", e)

    try:
        _notify_offerers_of_expired_collective_bookings()
    except Exception as e:
        logger.exception("Error in notify_offerers_of_expired_collective_bookings : %s", e)

    logger.info("[handle_expired_collective_bookings] End")


def _cancel_expired_collective_bookings(batch_size: int = 500) -> None:
    logger.info("[cancel_expired_collective_bookings] Start")

    expiring_collective_bookings_query = repository.find_expiring_collective_bookings_query()
    expiring_booking_ids = [
        b[0] for b in expiring_collective_bookings_query.with_entities(models.CollectiveBooking.id).all()
    ]

    logger.info("[cancel_expired_collective_bookings] %d expiring bookings to cancel", len(expiring_booking_ids))

    # we commit here to make sure there is no unexpected objects in SQLA cache before the update,
    # as we use synchronize_session=False
    db.session.commit()

    updated_total = 0
    start_index = 0

    while start_index < len(expiring_booking_ids):
        booking_to_update_ids = expiring_booking_ids[start_index : start_index + batch_size]
        updated = (
            db.session.query(models.CollectiveBooking)
            .filter(models.CollectiveBooking.id.in_(booking_to_update_ids))
            .update(
                {
                    "status": models.CollectiveBookingStatus.CANCELLED,
                    "cancellationReason": models.CollectiveBookingCancellationReasons.EXPIRED,
                    "cancellationDate": date_utils.get_naive_utc_now(),
                },
                synchronize_session=False,
            )
        )
        db.session.commit()

        logger.info(
            "[cancel_expired_collective_bookings] %d Bookings have been cancelled in this batch",
            updated,
        )

        updated_total += updated
        start_index += batch_size

    logger.info("[cancel_expired_collective_bookings] %d Bookings have been cancelled", updated_total)


def _notify_offerers_of_expired_collective_bookings() -> None:
    logger.info("[notify_offerers_of_expired_collective_bookings] Start")

    expired_collective_bookings = repository.find_expired_collective_bookings()

    for collective_booking in expired_collective_bookings:
        transactional_mails.send_eac_booking_cancellation_email(collective_booking)

    logger.info(
        "[notify_offerers_of_expired_collective_bookings] %d Offerers have been notified",
        len(expired_collective_bookings),
    )

    logger.info("[notify_offerers_of_expired_collective_bookings] End")
