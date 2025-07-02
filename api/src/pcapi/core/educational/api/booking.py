import datetime
import decimal
import logging
from functools import partial

import sqlalchemy.orm as sa_orm
from pydantic.v1.error_wrappers import ValidationError

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import schemas as educational_schemas
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational import validation
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.repository import find_pending_booking_confirmation_limit_date_in_3_days
from pcapi.core.educational.schemas import RedactorInformation
from pcapi.core.educational.serialization import collective_booking as collective_booking_serialize
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.repository.session_management import on_commit
from pcapi.routes.serialization import collective_bookings_serialize


logger = logging.getLogger(__name__)


def book_collective_offer(
    redactor_informations: RedactorInformation, stock_id: int
) -> educational_models.CollectiveBooking:
    redactor = educational_repository.find_or_create_redactor(redactor_informations)

    educational_institution = educational_repository.find_educational_institution_by_uai_code(redactor_informations.uai)
    if not educational_institution:
        raise exceptions.EducationalInstitutionUnknown()

    stock = educational_repository.get_and_lock_collective_stock(stock_id=stock_id)
    validation.check_collective_stock_is_bookable(stock)

    educational_year = educational_repository.find_educational_year_by_date(stock.startDatetime)
    if not educational_year:
        raise exceptions.EducationalYearNotFound()
    validation.check_user_can_prebook_collective_stock(redactor_informations.uai, stock)

    utcnow = datetime.datetime.utcnow()
    booking = educational_models.CollectiveBooking(
        educationalInstitution=educational_institution,
        educationalYear=educational_year,
        educationalRedactor=redactor,
        confirmationLimitDate=stock.bookingLimitDatetime,
        collectiveStockId=stock.id,
        venueId=stock.collectiveOffer.venueId,
        offererId=stock.collectiveOffer.venue.managingOffererId,
        status=educational_models.CollectiveBookingStatus.PENDING,
        dateCreated=utcnow,
        cancellationLimitDate=educational_utils.compute_educational_booking_cancellation_limit_date(
            stock.startDatetime, utcnow
        ),
    )
    db.session.add(booking)
    db.session.flush()

    logger.info(
        "Redactor booked a collective offer",
        extra={
            "redactor": redactor_informations.email,
            "offerId": stock.collectiveOfferId,
            "stockId": stock.id,
            "bookingId": booking.id,
        },
    )

    transactional_mails.send_eac_new_collective_prebooking_email_to_pro(booking)

    on_commit(partial(_notify_prebooking, data=collective_booking_serialize.serialize_collective_booking(booking)))

    return booking


def _notify_prebooking(data: educational_schemas.EducationalBookingResponse) -> None:
    try:
        adage_client.notify_prebooking(data=data)
    except AdageException as adage_error:
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


def confirm_collective_booking(educational_booking_id: int) -> educational_models.CollectiveBooking:
    collective_booking = educational_repository.find_collective_booking_by_id(educational_booking_id)

    if collective_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED:
        return collective_booking

    educational_utils.log_information_for_data_purpose(
        event_name="BookingApproval",
        extra_data={
            "stockId": collective_booking.collectiveStockId,
            "bookingId": educational_booking_id,
        },
        uai=None,
        user_role=None,
    )

    validation.check_collective_booking_status(collective_booking)
    validation.check_confirmation_limit_date_has_not_passed(collective_booking)

    educational_institution_id = collective_booking.educationalInstitutionId
    educational_year_id = collective_booking.educationalYearId
    deposit = educational_repository.get_and_lock_educational_deposit(educational_institution_id, educational_year_id)

    validation.check_institution_fund(
        educational_institution_id=educational_institution_id,
        educational_year_id=educational_year_id,
        booking_amount=collective_booking.collectiveStock.price,
        booking_date=collective_booking.collectiveStock.endDatetime,
        deposit=deposit,
    )
    if FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION.is_active():
        validation.check_ministry_fund(
            educational_year_id=educational_year_id,
            booking_amount=decimal.Decimal(collective_booking.collectiveStock.price),
            booking_date=collective_booking.collectiveStock.startDatetime,
            ministry=deposit.ministry,
        )

    collective_booking.mark_as_confirmed()

    db.session.add(collective_booking)
    db.session.flush()

    logger.info(
        "Head of institution confirmed an educational offer",
        extra={"collectiveBookingId": collective_booking.id},
    )

    transactional_mails.send_eac_new_booking_email_to_pro(collective_booking)

    return collective_booking


def refuse_collective_booking(educational_booking_id: int) -> educational_models.CollectiveBooking:
    collective_booking = educational_repository.find_collective_booking_by_id(educational_booking_id)
    if collective_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if collective_booking.status == educational_models.CollectiveBookingStatus.CANCELLED:
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


def get_collective_booking_report(
    *,
    user: User,
    booking_period: tuple[datetime.date, datetime.date] | None = None,
    status_filter: (
        educational_models.CollectiveBookingStatusFilter | None
    ) = educational_models.CollectiveBookingStatusFilter.BOOKED,
    event_date: datetime.datetime | None = None,
    venue_id: int | None = None,
    export_type: bookings_models.BookingExportType | None = bookings_models.BookingExportType.CSV,
) -> str | bytes:
    bookings_query = educational_repository.get_filtered_collective_booking_report(
        pro_user=user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
    )

    if export_type == bookings_models.BookingExportType.EXCEL:
        return collective_bookings_serialize.serialize_collective_booking_excel_report(bookings_query)
    return collective_bookings_serialize.serialize_collective_booking_csv_report(bookings_query)


def get_collective_booking_by_id(booking_id: int) -> educational_models.CollectiveBooking:
    collective_booking = (
        db.session.query(educational_models.CollectiveBooking)
        .filter(educational_models.CollectiveBooking.id == booking_id)
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock).load_only(
                educational_models.CollectiveStock.price,
                educational_models.CollectiveStock.startDatetime,
                educational_models.CollectiveStock.endDatetime,
                educational_models.CollectiveStock.numberOfTickets,
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .load_only(educational_models.CollectiveOffer.offerVenue, educational_models.CollectiveOffer.students),
            sa_orm.joinedload(educational_models.CollectiveBooking.educationalRedactor).load_only(
                educational_models.EducationalRedactor.id,
                educational_models.EducationalRedactor.email,
                educational_models.EducationalRedactor.civility,
                educational_models.EducationalRedactor.firstName,
                educational_models.EducationalRedactor.lastName,
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.educationalInstitution),
            sa_orm.joinedload(educational_models.CollectiveBooking.venue).load_only(
                offerers_models.Venue.postalCode,
                offerers_models.Venue.managingOffererId,
            ),
        )
        .options(
            sa_orm.load_only(
                educational_models.CollectiveBooking.id,
                educational_models.CollectiveBooking.venueId,
                educational_models.CollectiveBooking.offererId,
                educational_models.CollectiveBooking.status,
            )
        )
        .one_or_none()
    )
    if not collective_booking:
        raise exceptions.EducationalBookingNotFound()
    return collective_booking


def cancel_collective_offer_booking(offer_id: int, author_id: int, user_connect_as: bool) -> None:
    collective_offer: educational_models.CollectiveOffer | None = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.id == offer_id)
        .options(
            sa_orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            )
        )
        .first()
    )

    if collective_offer is None:
        raise exceptions.CollectiveOfferNotFound()

    validation.check_collective_offer_action_is_allowed(
        collective_offer, educational_models.CollectiveOfferAllowedAction.CAN_CANCEL
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
    bookings = educational_repository.find_bookings_starting_in_x_days(1)
    for booking in bookings:
        transactional_mails.send_eac_alert_one_day_before_event(booking)


def notify_pro_users_one_day_after() -> None:
    bookings = educational_repository.find_bookings_ending_in_x_days(-1)
    for booking in bookings:
        transactional_mails.send_eac_alert_one_day_after_event(booking)


def notify_pro_pending_booking_confirmation_limit_in_3_days() -> None:
    bookings = find_pending_booking_confirmation_limit_date_in_3_days()
    for booking in bookings:
        transactional_mails.send_eac_pending_booking_confirmation_limit_date_in_3_days(booking)


def _cancel_collective_booking(
    collective_booking: educational_models.CollectiveBooking,
    reason: educational_models.CollectiveBookingCancellationReasons,
    author_id: int,
) -> None:
    educational_repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
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
    collective_stock: educational_models.CollectiveStock,
    author_id: int,
    user_connect_as: bool,
) -> educational_models.CollectiveBooking:
    booking_to_cancel: educational_models.CollectiveBooking | None = next(
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
        cancellation_reason = educational_models.CollectiveBookingCancellationReasons.OFFERER_CONNECT_AS
    else:
        cancellation_reason = educational_models.CollectiveBookingCancellationReasons.OFFERER

    _cancel_collective_booking(booking_to_cancel, cancellation_reason, author_id)

    return booking_to_cancel


def cancel_collective_booking(
    collective_booking: educational_models.CollectiveBooking,
    reason: educational_models.CollectiveBookingCancellationReasons,
    force: bool = True,
    _from: str | None = None,
    author_id: int | None = None,
) -> None:
    collective_booking_id = collective_booking.id
    with atomic():
        educational_repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
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


def uncancel_collective_booking(collective_booking: educational_models.CollectiveBooking) -> None:
    educational_repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
    db.session.refresh(collective_booking)
    collective_booking.uncancel_booking()
    if collective_booking.status == educational_models.CollectiveBookingStatus.USED:
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
    collective_booking: educational_models.CollectiveBooking,
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
    institution_source: educational_models.EducationalInstitution,
    institution_destination: educational_models.EducationalInstitution,
) -> None:
    offers = db.session.query(educational_models.CollectiveOffer)
    offers = offers.join(educational_models.CollectiveStock)
    offers = offers.join(educational_models.CollectiveBooking)
    offers = offers.filter(educational_models.CollectiveBooking.id.in_(booking_ids))
    offers = offers.filter(educational_models.CollectiveBooking.educationalInstitution == institution_source)
    offer_ids = offers.with_entities(educational_models.CollectiveOffer.id)

    offers = db.session.query(educational_models.CollectiveOffer)
    offers = offers.filter(educational_models.CollectiveOffer.id.in_(offer_ids))
    offers.update({"institutionId": institution_destination.id}, synchronize_session=False)

    bookings = db.session.query(educational_models.CollectiveBooking)
    bookings = bookings.filter(educational_models.CollectiveBooking.id.in_(booking_ids))
    bookings = bookings.filter_by(educationalInstitution=institution_source)
    bookings.update({"educationalInstitutionId": institution_destination.id})

    db.session.flush()


def notify_redactor_that_booking_has_been_cancelled(booking: educational_schemas.EducationalBookingResponse) -> None:
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


def notify_pro_that_booking_has_been_cancelled(booking: educational_models.CollectiveBooking) -> None:
    transactional_mails.send_collective_booking_cancellation_confirmation_by_pro_email(booking)
