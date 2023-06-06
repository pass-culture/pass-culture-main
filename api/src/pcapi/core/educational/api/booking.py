import datetime
import decimal
import logging

from pydantic.error_wrappers import ValidationError
import sqlalchemy as sa

from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational import validation
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.repository import find_pending_booking_confirmation_limit_date_in_3_days
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.mails.transactional.educational.eac_booking_cancellation import send_eac_booking_cancellation_email
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking
from pcapi.routes.adage.v1.serialization.prebooking import serialize_reibursement_notification
from pcapi.routes.adage_iframe.serialization.adage_authentication import RedactorInformation
from pcapi.routes.serialization import collective_bookings_serialize


logger = logging.getLogger(__name__)


def book_collective_offer(
    redactor_informations: RedactorInformation, stock_id: int
) -> educational_models.CollectiveBooking:
    redactor = educational_repository.find_redactor_by_email(redactor_informations.email)
    if not redactor:
        redactor = _create_redactor(redactor_informations)

    educational_institution = educational_repository.find_educational_institution_by_uai_code(redactor_informations.uai)
    if not educational_institution:
        raise exceptions.EducationalInstitutionUnknown()

    # The call to transaction here ensures we free the FOR UPDATE lock
    # on the stock if validation issues an exception
    with transaction():
        stock = educational_repository.get_and_lock_collective_stock(stock_id=stock_id)
        validation.check_collective_stock_is_bookable(stock)

        educational_year = educational_repository.find_educational_year_by_date(stock.beginningDatetime)
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
                stock.beginningDatetime, utcnow
            ),
        )
        repository.save(booking)

    logger.info(
        "Redactor booked a collective offer",
        extra={
            "redactor": redactor_informations.email,
            "offerId": stock.collectiveOfferId,
            "stockId": stock.id,
            "bookingId": booking.id,
        },
    )

    if not transactional_mails.send_eac_new_collective_prebooking_email_to_pro(booking):
        logger.warning(
            "Could not send new prebooking email to pro",
            extra={"booking": booking.id},
        )

    search.async_index_collective_offer_ids([stock.collectiveOfferId])

    try:
        adage_client.notify_prebooking(data=prebooking.serialize_collective_booking(booking))
    except AdageException as adage_error:
        logger.error(
            "%s Educational institution will not receive a confirmation email.",
            adage_error.message,
            extra={
                "bookingId": booking.id,
                "adage status code": adage_error.status_code,
                "adage response text": adage_error.response_text,
            },
        )
    except ValidationError:
        logger.exception(
            "Could not notify adage of prebooking, hence send confirmation email to educational institution, as educationalBooking serialization failed.",
            extra={
                "bookingId": booking.id,
            },
        )

    return booking


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
    )

    validation.check_collective_booking_status(collective_booking)
    validation.check_confirmation_limit_date_has_not_passed(collective_booking)

    educational_institution_id = collective_booking.educationalInstitutionId
    educational_year_id = collective_booking.educationalYearId
    with transaction():
        deposit = educational_repository.get_and_lock_educational_deposit(
            educational_institution_id, educational_year_id
        )
        validation.check_institution_fund(
            educational_institution_id,
            educational_year_id,
            decimal.Decimal(collective_booking.collectiveStock.price),
            deposit,
        )
        if FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION.is_active():
            validation.check_ministry_fund(
                educational_year_id=educational_year_id,
                booking_amount=decimal.Decimal(collective_booking.collectiveStock.price),
                booking_date=collective_booking.collectiveStock.beginningDatetime,
                ministry=deposit.ministry,
            )

        collective_booking.mark_as_confirmed()

        db.session.add(collective_booking)
        db.session.commit()

    logger.info(
        "Head of institution confirmed an educational offer",
        extra={
            "collectiveBookingId": collective_booking.id,
        },
    )

    if not transactional_mails.send_eac_new_booking_email_to_pro(collective_booking):
        logger.warning(
            "Could not send new booking confirmation email to offerer",
            extra={"booking": collective_booking.id},
        )

    return collective_booking


def refuse_collective_booking(educational_booking_id: int) -> educational_models.CollectiveBooking:
    collective_booking = educational_repository.find_collective_booking_by_id(educational_booking_id)
    if collective_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if collective_booking.status == educational_models.CollectiveBookingStatus.CANCELLED:
        return collective_booking

    with transaction():
        try:
            collective_booking.mark_as_refused()
        except (
            exceptions.EducationalBookingNotRefusable,
            exceptions.CollectiveBookingAlreadyCancelled,
        ) as exception:
            logger.error(
                "User from adage trying to refuse collective booking that cannot be refused",
                extra={
                    "collective_booking_id": collective_booking.id,
                    "exception_type": exception.__class__.__name__,
                },
            )
            raise exception

        repository.save(collective_booking)

    logger.info(
        "Collective Booking has been cancelled",
        extra={
            "booking": collective_booking.id,
            "reason": str(collective_booking.cancellationReason),
        },
    )

    send_eac_booking_cancellation_email(collective_booking)

    search.async_index_collective_offer_ids([collective_booking.collectiveStock.collectiveOfferId])

    return collective_booking


def get_collective_booking_report(
    user: User,
    booking_period: tuple[datetime.date, datetime.date] | None = None,
    status_filter: educational_models.CollectiveBookingStatusFilter
    | None = educational_models.CollectiveBookingStatusFilter.BOOKED,
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
    query = educational_models.CollectiveBooking.query.filter(educational_models.CollectiveBooking.id == booking_id)
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock),
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock).joinedload(
            educational_models.CollectiveStock.collectiveOffer
        ),
        sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor),
        sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution),
        sa.orm.joinedload(educational_models.CollectiveBooking.venue),
    )
    collective_booking = query.one_or_none()
    if not collective_booking:
        raise exceptions.EducationalBookingNotFound()
    return collective_booking


def cancel_collective_offer_booking(offer_id: int) -> None:
    collective_offer: educational_models.CollectiveOffer | None = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == offer_id)
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            )
        )
        .first()
    )

    if collective_offer is None:
        raise exceptions.CollectiveOfferNotFound()

    if collective_offer.collectiveStock is None:
        raise exceptions.CollectiveStockNotFound()

    collective_stock = collective_offer.collectiveStock

    # Offer is reindexed in the end of this function
    cancelled_booking = _cancel_collective_booking_by_offerer(collective_stock)

    search.async_index_collective_offer_ids([offer_id])

    logger.info(
        "Cancelled collective booking from offer",
        extra={"collective_stock": collective_stock.id, "collective_booking": cancelled_booking.id},
    )

    try:
        adage_client.notify_booking_cancellation_by_offerer(data=serialize_collective_booking(cancelled_booking))
    except exceptions.AdageException as adage_error:
        logger.error(
            "%s Could not notify adage of collective booking cancellation by offerer. Educational institution won't be notified.",
            adage_error.message,
            extra={
                "collectiveBookingId": cancelled_booking.id,
                "adage status code": adage_error.status_code,
                "adage response text": adage_error.response_text,
            },
        )
    except ValidationError:
        logger.exception(
            "Could not notify adage of prebooking, hence send booking cancellation email to educational institution, as educationalBooking serialization failed.",
            extra={
                "collectiveBookingId": cancelled_booking.id,
            },
        )
    if not transactional_mails.send_collective_booking_cancellation_confirmation_by_pro_email(cancelled_booking):
        logger.warning(
            "Could not notify offerer about collective booking cancellation",
            extra={"collectiveStock": collective_stock.id},
        )


def notify_pro_users_one_day() -> None:
    bookings = educational_repository.find_bookings_happening_in_x_days(1)
    for booking in bookings:
        if not transactional_mails.send_eac_alert_one_day_before_event(booking):
            logger.warning(
                "Could not notify offerer one day before event",
                extra={"collectiveBooking": booking.id},
            )


def notify_pro_pending_booking_confirmation_limit_in_3_days() -> None:
    bookings = find_pending_booking_confirmation_limit_date_in_3_days()
    for booking in bookings:
        if not transactional_mails.send_eac_pending_booking_confirmation_limit_date_in_3_days(booking):
            logger.warning(
                "Could not notify offerer three days before booking confirmation limit date",
                extra={"collectiveBooking": booking.id},
            )


def _create_redactor(redactor_informations: RedactorInformation) -> educational_models.EducationalRedactor:
    redactor = educational_models.EducationalRedactor(
        email=redactor_informations.email,
        firstName=redactor_informations.firstname,
        lastName=redactor_informations.lastname,
        civility=redactor_informations.civility,
    )
    repository.save(redactor)
    return redactor


def _cancel_collective_booking(
    collective_booking: educational_models.CollectiveBooking,
    reason: educational_models.CollectiveBookingCancellationReasons,
) -> None:
    with transaction():
        educational_repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
        db.session.refresh(collective_booking)

        try:
            collective_booking.cancel_booking(reason)
        except exceptions.CollectiveBookingAlreadyCancelled:
            return

        db.session.commit()

    logger.info(
        "CollectiveBooking has been cancelled",
        extra={
            "collective_booking": collective_booking.id,
            "reason": str(reason),
        },
    )


def _cancel_collective_booking_by_offerer(
    collective_stock: educational_models.CollectiveStock,
) -> educational_models.CollectiveBooking:
    """
    Cancel booking.
    Note that this will not reindex the associated offer in Algolia
    """
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

    _cancel_collective_booking(
        booking_to_cancel,
        educational_models.CollectiveBookingCancellationReasons.OFFERER,
    )

    return booking_to_cancel


def cancel_collective_booking_by_id_from_support(
    collective_booking: educational_models.CollectiveBooking,
) -> None:
    with transaction():
        educational_repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
        db.session.refresh(collective_booking)
        if collective_booking.status == educational_models.CollectiveBookingStatus.REIMBURSED:
            raise exceptions.BookingIsAlreadyRefunded()
        if finance_repository.has_reimbursement(collective_booking):
            raise exceptions.BookingIsAlreadyRefunded()

        finance_api.cancel_pricing(collective_booking, finance_models.PricingLogReason.MARK_AS_UNUSED)
        collective_booking.cancel_booking(
            reason=educational_models.CollectiveBookingCancellationReasons.OFFERER,
            cancel_even_if_used=True,
        )

        db.session.commit()
    search.async_index_collective_offer_ids([collective_booking.collectiveStock.collectiveOfferId])
    logger.info(
        "CollectiveBooking has been cancelled by support",
        extra={
            "collective_booking": collective_booking.id,
            "reason": str(educational_models.CollectiveBookingCancellationReasons.OFFERER),
        },
    )


def uncancel_collective_booking_by_id_from_support(
    collective_booking: educational_models.CollectiveBooking,
) -> None:
    with transaction():
        educational_repository.get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
        db.session.refresh(collective_booking)
        collective_booking.uncancel_booking()
        db.session.commit()

    search.async_index_collective_offer_ids([collective_booking.collectiveStock.collectiveOfferId])
    logger.info(
        "CollectiveBooking has been uncancelled by support",
        extra={
            "collective_booking": collective_booking.id,
        },
    )


def notify_reimburse_collective_booking(booking_id: int, reason: str, value: float, details: str) -> None:
    booking = educational_repository.find_collective_booking_by_id(booking_id)
    if not booking:
        print(f"Collective booking {booking_id} not found")
        return
    price = booking.collectiveStock.price
    if value > price:
        print(f"Collective booking {booking_id} is priced at {price}. We cannot reimburse more than that.")
        return
    value = value or price
    adage_client.notify_reimburse_collective_booking(
        data=serialize_reibursement_notification(
            collective_booking=booking,
            reason=reason,
            value=value,
            details=details,
        ),
    )
    return
