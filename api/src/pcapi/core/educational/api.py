from datetime import datetime
import decimal
import logging
from typing import Optional

from pydantic.error_wrappers import ValidationError
from sqlalchemy.orm import joinedload

from pcapi.connectors.api_adage import AdageException
from pcapi.core import mails
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation
import pcapi.core.educational.adage_backends as adage_client
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.educational.models import EducationalYear
from pcapi.core.educational.models import Ministry
from pcapi.core.educational.utils import compute_educational_booking_cancellation_limit_date
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.educational.eac_new_booking_to_pro import send_eac_new_booking_email_to_pro
from pcapi.core.mails.transactional.educational.eac_new_prebooking_to_pro import send_eac_new_prebooking_email_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import validation as offer_validation
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import RedactorInformation
from pcapi.routes.serialization.stock_serialize import EducationalStockCreationBodyModel


logger = logging.getLogger(__name__)


def _create_redactor(redactor_informations: AuthenticatedInformation) -> EducationalRedactor:
    redactor = EducationalRedactor(
        email=redactor_informations.email,
        firstName=redactor_informations.firstname,
        lastName=redactor_informations.lastname,
        civility=redactor_informations.civility,
    )
    repository.save(redactor)
    return redactor


def book_educational_offer(redactor_informations: RedactorInformation, stock_id: int) -> EducationalBooking:
    redactor = educational_repository.find_redactor_by_email(redactor_informations.email)
    if not redactor:
        redactor = _create_redactor(redactor_informations)

    educational_institution = educational_repository.find_educational_institution_by_uai_code(redactor_informations.uai)
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
            quantity=1,
            token=bookings_repository.generate_booking_token(),
            venueId=stock.offer.venueId,
            offererId=stock.offer.venue.managingOffererId,
            status=bookings_models.BookingStatus.PENDING,
        )

        booking.dateCreated = datetime.utcnow()
        booking.cancellationLimitDate = compute_educational_booking_cancellation_limit_date(
            stock.beginningDatetime, booking.dateCreated
        )
        stock.dnBookedQuantity += booking.quantity

        repository.save(booking)

        create_collective_booking_with_collective_stock(
            stock_id, booking.id, educational_institution, educational_year, redactor
        )

    logger.info(
        "Redactor booked an educational offer",
        extra={
            "redactor": redactor_informations.email,
            "offerId": stock.offerId,
            "stockId": stock.id,
            "bookingId": booking.id,
        },
    )

    if not send_eac_new_prebooking_email_to_pro(stock, booking):
        logger.warning(
            "Could not send new prebooking email to pro",
            extra={"booking": booking.id},
        )

    search.async_index_offer_ids([stock.offerId])

    try:
        adage_client.notify_prebooking(data=serialize_educational_booking(booking.educationalBooking))
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
            "Coulf not notify adage of prebooking, hence send confirmation email to educational institution, as educationalBooking serialization failed.",
            extra={
                "bookingId": booking.id,
            },
        )

    return booking


def create_collective_booking_with_collective_stock(
    stock_id: str,
    booking_id: str,
    educational_institution: EducationalInstitution,
    educational_year: EducationalYear,
    redactor: EducationalRedactor,
) -> Optional[CollectiveBooking]:
    with transaction():
        collective_stock = offers_repository.get_and_lock_collective_stock(stock_id=stock_id)

        # TODO: remove this once this code is on production
        # and all data has been migrated to the new models
        if not collective_stock:
            return None

        validation.check_collective_stock_is_bookable(collective_stock)

        collective_booking = CollectiveBooking(
            collectiveStockId=collective_stock.id,
            venueId=collective_stock.collectiveOffer.venueId,
            offererId=collective_stock.collectiveOffer.venue.managingOffererId,
            status=CollectiveBookingStatus.PENDING,
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            confirmationLimitDate=collective_stock.bookingLimitDatetime,
            educationalRedactor=redactor,
        )

        collective_booking.dateCreated = datetime.utcnow()
        collective_booking.cancellationLimitDate = compute_educational_booking_cancellation_limit_date(
            collective_stock.beginningDatetime, collective_booking.dateCreated
        )
        collective_booking.bookingId = booking_id

        db.session.add(collective_booking)
        db.session.commit()

        return collective_booking


def confirm_educational_booking(educational_booking_id: int) -> EducationalBooking:
    educational_booking = educational_repository.find_educational_booking_by_id(educational_booking_id)
    if educational_booking is None:
        raise exceptions.EducationalBookingNotFound()

    booking: bookings_models.Booking = educational_booking.booking
    if booking.status == bookings_models.BookingStatus.CONFIRMED:
        return educational_booking

    validation.check_educational_booking_status(educational_booking)
    validation.check_confirmation_limit_date_has_not_passed(educational_booking)

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

    logger.info(
        "Head of institution confirmed an educational offer",
        extra={
            "bookingId": booking.id,
        },
    )

    if not send_eac_new_booking_email_to_pro(booking):
        logger.warning(
            "Could not send new booking confirmation email to offerer",
            extra={"booking": booking.id},
        )

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

    booking_email = booking.stock.offer.bookingEmail
    if booking_email:
        data = SendinblueTransactionalEmailData(
            template=TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION.value,
            params={
                "OFFER_NAME": stock.offer.name,
                "EVENT_BEGINNING_DATETIME": stock.beginningDatetime.strftime("%d/%m/%Y à %H:%M"),
                "EDUCATIONAL_REDACTOR_EMAIL": educational_booking.educationalRedactor.email,
            },
        )
        mails.send(recipients=[booking_email], data=data)

    search.async_index_offer_ids([stock.offerId])

    return educational_booking


def create_educational_institution(institution_id: str) -> EducationalInstitution:
    educational_institution = EducationalInstitution(institutionId=institution_id)
    repository.save(educational_institution)

    return educational_institution


def update_educational_institution_data(
    institution_id: str, institution_data: dict[str, str]
) -> EducationalInstitution:
    educational_institution = EducationalInstitution.query.filter_by(institutionId=institution_id).one()
    educational_institution.name = institution_data["name"]
    educational_institution.city = institution_data["city"]
    educational_institution.postalCode = institution_data["postalCode"]
    educational_institution.email = institution_data["email"]
    educational_institution.phoneNumber = institution_data["phoneNumber"]

    return educational_institution


def create_educational_deposit(
    educational_year_id: str, educational_institution_id: int, deposit_amount: int, ministry: Ministry
) -> EducationalDeposit:
    educational_deposit = EducationalDeposit(
        educationalYearId=educational_year_id,
        educationalInstitutionId=educational_institution_id,
        amount=decimal.Decimal(deposit_amount),
        isFinal=False,
        dateCreated=datetime.utcnow(),
        ministry=ministry,
    )
    repository.save(educational_deposit)

    return educational_deposit


def get_venues_by_siret(siret: str) -> list[offerers_models.Venue]:
    venue = offerers_models.Venue.query.filter_by(siret=siret).one()
    return [venue]


def get_educational_categories() -> dict:
    educational_subcategories = [
        subcategory for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.can_be_educational == True
    ]
    educational_categories_ids = list(set(subcategory.category_id for subcategory in educational_subcategories))
    educational_categories = [
        category for category in categories.ALL_CATEGORIES if category.id in educational_categories_ids
    ]

    return {"subcategories": educational_subcategories, "categories": educational_categories}


def notify_educational_redactor_on_educational_offer_or_stock_edit(
    offer_id: str,
    updated_fields: list[str],
) -> None:
    if len(updated_fields) == 0:
        return

    active_educational_bookings = educational_repository.find_active_educational_booking_by_offer_id(offer_id)
    if active_educational_bookings is None:
        return

    data = EducationalBookingEdition(
        **serialize_educational_booking(active_educational_bookings).dict(),
        updatedFields=updated_fields,
    )
    try:
        adage_client.notify_offer_or_stock_edition(data)
    except AdageException as exception:
        logger.error(
            "Error while sending notification to Adage",
            extra={
                "adage_response_message": exception.message,
                "adage_response_status_code": exception.status_code,
                "adage_response_response_text": exception.response_text,
                "data": data.dict(),
            },
        )


def create_collective_stock(
    stock_data: EducationalStockCreationBodyModel, user: User, *, legacy_id: Optional[int] = None
) -> Optional[CollectiveStock]:
    from pcapi.core.offers.api import _update_offer_fraud_information

    offer_id = stock_data.offer_id
    beginning = stock_data.beginning_datetime
    booking_limit_datetime = stock_data.booking_limit_datetime
    total_price = stock_data.total_price
    number_of_tickets = stock_data.number_of_tickets
    educational_price_detail = stock_data.educational_price_detail

    if legacy_id:  # FIXME (rpaoloni, 2022-03-7): Remove legacy support layer
        collective_offer = (
            CollectiveOffer.query.filter_by(offerId=offer_id)
            .options(joinedload(CollectiveOffer.collectiveStock))
            .one_or_none()
        )
        if not collective_offer:
            return None
    else:
        collective_offer = (
            CollectiveOffer.query.filter_by(id=offer_id).options(joinedload(CollectiveOffer.collectiveStock)).one()
        )
    if collective_offer.collectiveStock:
        raise exceptions.CollectiveStockAlreadyExists()

    offer_validation.check_validation_status(collective_offer)
    if booking_limit_datetime is None:
        booking_limit_datetime = beginning

    collective_stock = CollectiveStock(
        collectiveOffer=collective_offer,
        beginningDatetime=beginning,
        bookingLimitDatetime=booking_limit_datetime,
        price=total_price,
        numberOfTickets=number_of_tickets,
        priceDetail=educational_price_detail,
        stockId=legacy_id if legacy_id else None,  # FIXME (rpaoloni, 2022-03-7): Remove legacy support layer
    )
    repository.save(collective_stock)
    logger.info(
        "Collective stock has been created",
        extra={"collective_offer": collective_offer.id, "collective_stock_id": collective_stock.id},
    )

    if FeatureToggle.ENABLE_NEW_COLLECTIVE_MODEL.is_active():
        if collective_offer.validation == OfferValidationStatus.DRAFT:
            _update_offer_fraud_information(collective_offer, user)
    else:
        collective_offer.validation = OfferValidationStatus.APPROVED
        collective_offer.lastValidationDate = datetime.now()
        repository.save(collective_offer)

    if not legacy_id:
        search.async_index_offer_ids([collective_offer.id])
    return collective_stock
