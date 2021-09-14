from datetime import datetime
import decimal
import logging

from pcapi.connectors.api_adage import get_institutional_project_redactor_by_email
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.bookings.api import compute_cancellation_limit_date
from pcapi.core.educational import exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.offers import repository as offers_repository
from pcapi.models import db
from pcapi.repository import repository
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

EAC_DEFAULT_BOOKED_QUANTITY = 1


def create_redactor_from_email(redactor_email: str) -> EducationalRedactor:
    educational_redactor_information = get_institutional_project_redactor_by_email(redactor_email)
    redactor = EducationalRedactor(
        email=educational_redactor_information.email,
        firstName=educational_redactor_information.first_name,
        lastName=educational_redactor_information.last_name,
        civility=educational_redactor_information.civility,
    )
    repository.save(redactor)
    return redactor


def book_educational_offer(redactor_email: str, uai_code: str, stock_id: int) -> EducationalBooking:
    redactor = educational_repository.find_redactor_by_email(redactor_email)
    if not redactor:
        redactor = create_redactor_from_email(redactor_email)

    educational_institution = educational_repository.find_educational_institution_by_uai_code(uai_code)
    validation.check_institution_exists(educational_institution)

    # The call to transaction here ensures we free the FOR UPDATE lock
    # on the stock if validation issues an exception
    with transaction():
        stock = offers_repository.get_and_lock_stock(stock_id=stock_id)
        validation.check_stock_is_bookable(stock)

        educational_year = educational_repository.find_educational_year_by_date(stock.beginningDatetime)
        validation.check_educational_year_exists(educational_year)

        educational_booking = EducationalBooking(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalRedactor=redactor,
            confirmationLimitDate=stock.bookingLimitDatetime,
        )

        booking = bookings_models.Booking(
            educationalBooking=educational_booking,
            stockId=stock.id,
            amount=stock.price,
            token=bookings_repository.generate_booking_token(),
            venueId=stock.offer.venueId,
            offererId=stock.offer.venue.managingOffererId,
            status=bookings_models.BookingStatus.PENDING,
        )

        booking.dateCreated = datetime.utcnow()
        booking.cancellationLimitDate = compute_cancellation_limit_date(stock.beginningDatetime, booking.dateCreated)
        stock.dnBookedQuantity += EAC_DEFAULT_BOOKED_QUANTITY

        repository.save(booking)

    logger.info(
        "Redactor booked an educational offer",
        extra={
            "redactor": redactor_email,
            "offerId": stock.offerId,
            "stockId": stock.id,
            "bookingId": booking.id,
        },
    )

    search.async_index_offer_ids([stock.offerId])

    return booking


def confirm_educational_booking(educational_booking_id: int) -> EducationalBooking:
    educational_booking = educational_repository.find_educational_booking_by_id(educational_booking_id)
    if educational_booking is None:
        raise exceptions.EducationalBookingNotFound()

    booking: bookings_models.Booking = educational_booking.booking
    if booking.status == bookings_models.BookingStatus.CONFIRMED:
        return educational_booking

    validation.check_educational_booking_status(educational_booking)

    educational_institution_id = educational_booking.educationalInstitutionId
    educational_year_id = educational_booking.educationalYearId
    with transaction():
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
        repository.save(booking)

    return educational_booking


def mark_educational_booking_as_used_by_institute(educational_booking_id: int) -> EducationalBooking:
    educational_booking = educational_repository.find_educational_booking_by_id(educational_booking_id)
    if educational_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if educational_booking.status == EducationalBookingStatus.USED_BY_INSTITUTE:
        return educational_booking

    try:
        educational_booking.mark_as_used_by_institute()
    except exceptions.EducationalBookingNotConfirmedYet as exception:
        logger.error(
            "User from adage trying to mark unconfirmed educational booking",
            extra={"educational_booking_id": educational_booking_id},
        )
        raise exception
    repository.save(educational_booking)

    return educational_booking


def refuse_educational_booking(educational_booking_id: int) -> EducationalBooking:
    educational_booking = educational_repository.find_educational_booking_by_id(educational_booking_id)

    if educational_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if educational_booking.status == EducationalBookingStatus.REFUSED:
        return educational_booking

    with transaction():
        stock = offers_repository.get_and_lock_stock(stock_id=educational_booking.booking.stockId)
        booking = educational_booking.booking
        db.session.refresh(educational_booking.booking)

        try:
            educational_booking.mark_as_refused()
        except (
            exceptions.EducationalBookingNotRefusable,
            exceptions.EducationalBookingAlreadyCancelled,
        ) as exception:
            logger.error(
                "User from adage trying to refuse educational booking that cannot be refused",
                extra={
                    "educational_booking_id": educational_booking_id,
                    "exception_type": exception.__class__.__name__,
                },
            )
            raise exception

        stock.dnBookedQuantity -= booking.quantity

        repository.save(booking, educational_booking)

    logger.info(
        "Booking has been cancelled",
        extra={
            "booking": booking.id,
            "reason": str(booking.cancellationReason),
        },
    )

    search.async_index_offer_ids([stock.offerId])

    return educational_booking


def create_educational_institution(institution_id: str) -> EducationalInstitution:
    educational_institution = EducationalInstitution(institutionId=institution_id)
    repository.save(educational_institution)

    return educational_institution


def create_educational_deposit(
    educational_year_id: str,
    educational_institution_id: int,
    deposit_amount: int,
) -> EducationalDeposit:
    educational_deposit = EducationalDeposit(
        educationalYearId=educational_year_id,
        educationalInstitutionId=educational_institution_id,
        amount=decimal.Decimal(deposit_amount),
        isFinal=False,
        dateCreated=datetime.utcnow(),
    )
    repository.save(educational_deposit)

    return educational_deposit
