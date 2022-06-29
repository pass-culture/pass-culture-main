import datetime
import decimal
import logging
from operator import or_
from typing import Iterable
from typing import Optional
from typing import Union
from typing import cast

from flask_sqlalchemy import BaseQuery
from pydantic.error_wrappers import ValidationError
import sqlalchemy as sqla
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.elements import not_

from pcapi import settings
from pcapi.core import mails
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.bookings.models import BookingExportType
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation
import pcapi.core.educational.adage_backends as adage_client
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveBookingStatusFilter
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.repository import get_and_lock_collective_stock
from pcapi.core.educational.repository import get_collective_offers_for_filters
from pcapi.core.educational.repository import get_collective_offers_template_for_filters
from pcapi.core.educational.repository import get_filtered_collective_booking_report
from pcapi.core.educational.utils import compute_educational_booking_cancellation_limit_date
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.educational.eac_new_booking_to_pro import send_eac_new_booking_email_to_pro
from pcapi.core.mails.transactional.educational.eac_new_prebooking_to_pro import (
    send_eac_new_collective_prebooking_email_to_pro,
)
from pcapi.core.mails.transactional.educational.eac_new_prebooking_to_pro import send_eac_new_prebooking_email_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import validation as offer_validation
from pcapi.core.offers.models import Stock
from pcapi.core.offers.utils import as_utc_without_timezone
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking
from pcapi.routes.adage_iframe.serialization.adage_authentication import RedactorInformation
from pcapi.routes.serialization.collective_bookings_serialize import serialize_collective_booking_csv_report
from pcapi.routes.serialization.collective_bookings_serialize import serialize_collective_booking_excel_report
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferBodyModel
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.routes.serialization.offers_serialize import PostEducationalOfferBodyModel
from pcapi.routes.serialization.stock_serialize import EducationalStockCreationBodyModel
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_raise_error


logger = logging.getLogger(__name__)
OFFERS_RECAP_LIMIT = 501


def _create_redactor(redactor_informations: RedactorInformation) -> educational_models.EducationalRedactor:
    redactor = educational_models.EducationalRedactor(
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

        educational_year = educational_repository.find_educational_year_by_date(stock.beginningDatetime)  # type: ignore [arg-type]
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

        booking.dateCreated = datetime.datetime.utcnow()
        booking.cancellationLimitDate = compute_educational_booking_cancellation_limit_date(
            stock.beginningDatetime, booking.dateCreated  # type: ignore [arg-type]
        )
        stock.dnBookedQuantity += booking.quantity

        repository.save(booking)

        collective_stock = db.session.query(CollectiveStock.id).filter_by(stockId=stock_id).one_or_none()
        if collective_stock:
            create_collective_booking_with_collective_stock(
                collective_stock.id, booking.id, educational_institution, educational_year, redactor  # type: ignore [arg-type]
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
        adage_client.notify_prebooking(data=serialize_educational_booking(booking.educationalBooking))  # type: ignore [arg-type]
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


def book_collective_offer(redactor_informations: RedactorInformation, stock_id: int) -> CollectiveBooking:
    redactor = educational_repository.find_redactor_by_email(redactor_informations.email)
    if not redactor:
        redactor = _create_redactor(redactor_informations)

    educational_institution = educational_repository.find_educational_institution_by_uai_code(redactor_informations.uai)
    validation.check_institution_exists(educational_institution)

    # The call to transaction here ensures we free the FOR UPDATE lock
    # on the stock if validation issues an exception
    with transaction():
        stock = educational_repository.get_and_lock_collective_stock(stock_id=stock_id)
        validation.check_collective_stock_is_bookable(stock)

        educational_year = educational_repository.find_educational_year_by_date(stock.beginningDatetime)
        validation.check_educational_year_exists(educational_year)
        validation.check_user_can_prebook_collective_stock(redactor_informations.uai, stock)

        utcnow = datetime.datetime.utcnow()
        booking = CollectiveBooking(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalRedactor=redactor,
            confirmationLimitDate=stock.bookingLimitDatetime,
            collectiveStockId=stock.id,
            venueId=stock.collectiveOffer.venueId,
            offererId=stock.collectiveOffer.venue.managingOffererId,
            status=educational_models.CollectiveBookingStatus.PENDING,
            dateCreated=utcnow,
            cancellationLimitDate=compute_educational_booking_cancellation_limit_date(stock.beginningDatetime, utcnow),
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

    if not send_eac_new_collective_prebooking_email_to_pro(booking):
        logger.warning(
            "Could not send new prebooking email to pro",
            extra={"booking": booking.id},
        )

    search.async_index_collective_offer_ids([stock.collectiveOfferId])

    try:
        adage_client.notify_prebooking(data=serialize_collective_booking(booking))
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
    stock_id: Union[int, str],
    booking_id: str,
    educational_institution: educational_models.EducationalInstitution,
    educational_year: educational_models.EducationalYear,
    redactor: educational_models.EducationalRedactor,
) -> Optional[CollectiveBooking]:
    with transaction():
        collective_stock = get_and_lock_collective_stock(stock_id=stock_id)  # type: ignore [arg-type]

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

        collective_booking.dateCreated = datetime.datetime.utcnow()
        collective_booking.cancellationLimitDate = compute_educational_booking_cancellation_limit_date(
            collective_stock.beginningDatetime, collective_booking.dateCreated
        )
        collective_booking.bookingId = booking_id  # type: ignore [assignment]

        db.session.add(collective_booking)
        db.session.commit()

        return collective_booking


def confirm_collective_booking(educational_booking_id: int) -> CollectiveBooking:
    collective_booking = educational_repository.find_collective_booking_by_id(educational_booking_id)

    if collective_booking is None:
        raise exceptions.EducationalBookingNotFound()

    if collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED:
        return collective_booking

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
            collective_booking.collectiveStock.price,
            deposit,
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

    if not send_eac_new_booking_email_to_pro(collective_booking):
        logger.warning(
            "Could not send new booking confirmation email to offerer",
            extra={"booking": collective_booking.id},
        )

    return collective_booking


def refuse_collective_booking(educational_booking_id: int) -> CollectiveBooking:

    collective_booking = educational_repository.find_collective_booking_by_id(educational_booking_id)
    if collective_booking is None:
        raise exceptions.EducationalBookingNotFound()

    collective_booking = cast(CollectiveBooking, collective_booking)  # we already checked it was not None

    if collective_booking.status == CollectiveBookingStatus.CANCELLED:
        return collective_booking

    with transaction():
        try:
            collective_booking.mark_as_refused()
        except (
            exceptions.EducationalBookingNotRefusable,
            exceptions.EducationalBookingAlreadyCancelled,
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

    booking_email = collective_booking.collectiveStock.collectiveOffer.bookingEmail
    if booking_email:
        collective_stock = collective_booking.collectiveStock
        data = SendinblueTransactionalEmailData(
            template=TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION.value,
            params={
                "OFFER_NAME": collective_stock.collectiveOffer.name,
                "EDUCATIONAL_INSTITUTION_NAME": collective_booking.educationalInstitution.name,
                "VENUE_NAME": collective_stock.collectiveOffer.venue.name,
                "EVENT_DATE": collective_stock.beginningDatetime.strftime("%d/%m/%Y"),
                "EVENT_HOUR": collective_stock.beginningDatetime.strftime("%H:%M"),
                "REDACTOR_FIRSTNAME": collective_booking.educationalRedactor.firstName,
                "REDACTOR_LASTNAME": collective_booking.educationalRedactor.lastName,
                "REDACTOR_EMAIL": collective_booking.educationalRedactor.email,
                "EDUCATIONAL_INSTITUTION_CITY": collective_booking.educationalInstitution.city,
                "EDUCATIONAL_INSTITUTION_POSTAL_CODE": collective_booking.educationalInstitution.postalCode,
            },
        )
        mails.send(recipients=[booking_email], data=data)

    search.async_index_collective_offer_ids([collective_booking.collectiveStock.collectiveOfferId])

    return collective_booking


def create_educational_institution(
    institution_id: str,
    institution_data: dict[str, str],
) -> educational_models.EducationalInstitution:
    educational_institution = educational_models.EducationalInstitution(
        institutionId=institution_id,
        name=institution_data["name"],
        city=institution_data["city"],
        postalCode=institution_data["postalCode"],
        email=institution_data["email"],
        phoneNumber=institution_data["phoneNumber"],
    )
    repository.save(educational_institution)

    return educational_institution


def update_educational_institution_data(
    institution_id: str, institution_data: dict[str, str]
) -> educational_models.EducationalInstitution:
    educational_institution = educational_models.EducationalInstitution.query.filter_by(
        institutionId=institution_id
    ).one()
    educational_institution.name = institution_data["name"]
    educational_institution.city = institution_data["city"]
    educational_institution.postalCode = institution_data["postalCode"]
    educational_institution.email = institution_data["email"]
    educational_institution.phoneNumber = institution_data["phoneNumber"]

    return educational_institution


def create_educational_deposit(
    educational_year_id: str,
    educational_institution_id: int,
    deposit_amount: int,
    ministry: educational_models.Ministry,
) -> educational_models.EducationalDeposit:
    educational_deposit = educational_models.EducationalDeposit(
        educationalYearId=educational_year_id,
        educationalInstitutionId=educational_institution_id,
        amount=decimal.Decimal(deposit_amount),
        isFinal=False,
        dateCreated=datetime.datetime.utcnow(),
        ministry=ministry,
    )
    repository.save(educational_deposit)

    return educational_deposit


def get_venues_by_siret(siret: str) -> list[offerers_models.Venue]:
    venue = (
        offerers_models.Venue.query.filter_by(siret=siret, isVirtual=False)
        .options(joinedload(offerers_models.Venue.contact))
        .one()
    )
    return [venue]


def get_all_venues(page: Optional[int], per_page: Optional[int]) -> list[offerers_models.Venue]:
    page = 1 if page is None else page
    per_page = 1000 if per_page is None else per_page

    return (
        offerers_models.Venue.query.filter_by(isVirtual=False)
        .order_by(offerers_models.Venue.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .options(joinedload(offerers_models.Venue.contact))
        .all()
    )


def get_venues_by_name(name: str) -> list[offerers_models.Venue]:
    name = name.replace(" ", "%")
    name = name.replace("-", "%")
    name = clean_accents(name)
    venues = (
        offerers_models.Venue.query.filter(
            or_(
                sqla.func.unaccent(offerers_models.Venue.name).ilike(f"%{name}%"),
                sqla.func.unaccent(offerers_models.Venue.publicName).ilike(f"%{name}%"),
            )
        )
        .filter(offerers_models.Venue.isVirtual.is_(False))
        .options(joinedload(offerers_models.Venue.contact))
        .all()
    )
    return venues


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


def notify_educational_redactor_on_collective_offer_or_stock_edit(
    collective_offer_id: int,
    updated_fields: list[str],
) -> None:
    if len(updated_fields) == 0:
        return

    active_collective_bookings = educational_repository.find_active_collective_booking_by_offer_id(collective_offer_id)
    if active_collective_bookings is None:
        return

    data = EducationalBookingEdition(
        **serialize_collective_booking(active_collective_bookings).dict(),
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


def _update_educational_booking_educational_year_id(
    booking: Union[bookings_models.Booking, educational_models.CollectiveBooking],
    new_beginning_datetime: datetime.datetime,
) -> None:
    educational_year = educational_repository.find_educational_year_by_date(new_beginning_datetime)

    if educational_year is None:
        raise exceptions.EducationalYearNotFound()

    if isinstance(booking, educational_models.CollectiveBooking):
        booking.educationalYear = educational_year
    else:
        educational_booking = booking.educationalBooking
        if educational_booking is None:
            return
        educational_booking.educationalYear = educational_year


def edit_collective_stock(stock: CollectiveStock, stock_data: dict) -> CollectiveStock:
    from pcapi.core.offers.api import _update_educational_booking_cancellation_limit_date

    beginning = stock_data.get("beginningDatetime")
    beginning = as_utc_without_timezone(beginning) if beginning else None
    booking_limit_datetime = stock_data.get("bookingLimitDatetime")
    booking_limit_datetime = as_utc_without_timezone(booking_limit_datetime) if booking_limit_datetime else None

    updatable_fields = _extract_updatable_fields_from_stock_data(stock, stock_data, beginning, booking_limit_datetime)

    offer_validation.check_booking_limit_datetime(stock, beginning, booking_limit_datetime)

    # due to check_booking_limit_datetime the only reason beginning < booking_limit_dt is when they are on the same day
    # in the venue timezone
    if beginning is not None and beginning < updatable_fields["bookingLimitDatetime"]:
        updatable_fields["bookingLimitDatetime"] = updatable_fields["beginningDatetime"]

    collective_stock_unique_booking = CollectiveBooking.query.filter(
        CollectiveBooking.collectiveStockId == stock.id,
        not_(CollectiveBooking.status == CollectiveBookingStatus.CANCELLED),
    ).one_or_none()

    if collective_stock_unique_booking:
        validation.check_collective_booking_status_pending(collective_stock_unique_booking)

        collective_stock_unique_booking.confirmationLimitDate = updatable_fields["bookingLimitDatetime"]

        if beginning:
            _update_educational_booking_cancellation_limit_date(collective_stock_unique_booking, beginning)
            _update_educational_booking_educational_year_id(collective_stock_unique_booking, beginning)

        if stock_data.get("price"):
            collective_stock_unique_booking.amount = stock_data.get("price")

    validation.check_collective_stock_is_editable(stock)

    with transaction():
        stock = get_and_lock_collective_stock(stock_id=stock.id)
        for attribute, new_value in updatable_fields.items():
            if new_value is not None and getattr(stock, attribute) != new_value:
                setattr(stock, attribute, new_value)
        db.session.add(stock)
        db.session.commit()

    logger.info("Stock has been updated", extra={"stock": stock.id})
    search.async_index_collective_offer_ids([stock.collectiveOfferId])

    notify_educational_redactor_on_collective_offer_or_stock_edit(
        stock.collectiveOffer.id,
        list(stock_data.keys()),
    )

    db.session.refresh(stock)
    return stock


def _extract_updatable_fields_from_stock_data(
    stock: CollectiveStock, stock_data: dict, beginning: datetime, booking_limit_datetime: datetime  # type: ignore [valid-type]
) -> dict:
    # if booking_limit_datetime is provided but null, set it to default value which is event datetime
    if "bookingLimitDatetime" in stock_data.keys() and booking_limit_datetime is None:
        booking_limit_datetime = beginning if beginning else stock.beginningDatetime

    if "bookingLimitDatetime" not in stock_data.keys():
        booking_limit_datetime = stock.bookingLimitDatetime

    updatable_fields = {
        "beginningDatetime": beginning,
        "bookingLimitDatetime": booking_limit_datetime,
        "price": stock_data.get("price"),
        "numberOfTickets": stock_data.get("numberOfTickets"),
        "priceDetail": stock_data.get("educationalPriceDetail"),
    }

    return updatable_fields


def create_collective_stock(
    stock_data: Union[
        CollectiveStockCreationBodyModel,
        EducationalStockCreationBodyModel,
    ],
    user: User,
    *,
    legacy_id: Optional[int] = None,
    offer_id: Optional[int] = None,
) -> Optional[CollectiveStock]:
    from pcapi.core.offers.api import update_offer_fraud_information

    offer_id = offer_id or stock_data.offer_id
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

    validation.check_collective_offer_number_of_collective_stocks(collective_offer)
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
    db.session.add(collective_stock)
    db.session.commit()
    logger.info(
        "Collective stock has been created",
        extra={"collective_offer": collective_offer.id, "collective_stock_id": collective_stock.id},
    )

    if (
        not FeatureToggle.ENABLE_EDUCATIONAL_INSTITUTION_ASSOCIATION.is_active()
        and collective_offer.validation == OfferValidationStatus.DRAFT
    ):
        update_offer_fraud_information(collective_offer, user)
    search.async_index_collective_offer_ids([collective_offer.id])

    return collective_stock


def unindex_expired_collective_offers(process_all_expired: bool = False) -> None:
    """Unindex collective offers that have expired.

    By default, process collective offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles collective offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included).

    If ``process_all_expired`` is true, process... well all expired
    collective offers.
    """
    start_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    interval = [start_of_day - datetime.timedelta(days=2), start_of_day]
    if process_all_expired:
        interval[0] = datetime.datetime(2000, 1, 1)  # arbitrary old date

    page = 0
    limit = settings.ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE
    while collective_offer_ids := _get_expired_collective_offer_ids(interval, page, limit):
        logger.info("[ALGOLIA] Found %d expired collective offers to unindex", len(collective_offer_ids))
        search.unindex_collective_offer_ids(collective_offer_ids)
        page += 1


def _get_expired_collective_offer_ids(interval: list[datetime.datetime], page: int, limit: int) -> list[int]:
    collective_offers = educational_repository.get_expired_collective_offers(interval)
    collective_offers = collective_offers.offset(page * limit).limit(limit)
    return [offer_id for offer_id, in collective_offers.with_entities(educational_models.CollectiveOffer.id)]


def get_collective_booking_report(
    user: User,
    booking_period: Optional[tuple[datetime.date, datetime.date]] = None,
    status_filter: Optional[CollectiveBookingStatusFilter] = CollectiveBookingStatusFilter.BOOKED,
    event_date: Optional[datetime.datetime] = None,
    venue_id: Optional[int] = None,
    export_type: Optional[BookingExportType] = BookingExportType.CSV,
) -> Union[str, bytes]:
    bookings_query = get_filtered_collective_booking_report(
        pro_user=user,
        period=booking_period,  # type: ignore [arg-type]
        status_filter=status_filter,  # type: ignore [arg-type]
        event_date=event_date,
        venue_id=venue_id,
    )

    if export_type == BookingExportType.EXCEL:
        return serialize_collective_booking_excel_report(bookings_query)
    return serialize_collective_booking_csv_report(bookings_query)


def list_collective_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    category_id: Optional[str],
    offerer_id: Optional[int],
    venue_id: Optional[int] = None,
    name_keywords: Optional[str] = None,
    status: Optional[str] = None,
    period_beginning_date: Optional[str] = None,
    period_ending_date: Optional[str] = None,
) -> list[Union[CollectiveOffer, CollectiveOfferTemplate]]:
    offers = get_collective_offers_for_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offers_limit=OFFERS_RECAP_LIMIT,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords=name_keywords,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
    )
    templates = get_collective_offers_template_for_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offers_limit=OFFERS_RECAP_LIMIT,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords=name_keywords,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
    )
    offer_index = 0
    template_index = 0
    merged_offers = []

    # merge two ordered lists to one shorter than OFFERS_RECAP_LIMIT items
    for _ in range(min(OFFERS_RECAP_LIMIT, (len(offers) + len(templates)))):

        if offer_index >= len(offers) and template_index >= len(templates):
            # this should never hapen. Only there as defensive mesure.
            break

        if offer_index >= len(offers):
            merged_offers.append(templates[template_index])
            template_index += 1
            continue

        if template_index >= len(templates):
            merged_offers.append(offers[offer_index])
            offer_index += 1
            continue

        offer_date = offers[offer_index].dateCreated
        template_date = templates[template_index].dateCreated

        if offer_date > template_date:
            merged_offers.append(offers[offer_index])
            offer_index += 1
        else:
            merged_offers.append(templates[template_index])
            template_index += 1

    return merged_offers


def get_educational_domains_from_ids(
    educational_domain_ids: Optional[list[int]],
) -> list[educational_models.EducationalDomain]:
    if educational_domain_ids is None:
        return []

    unique_educational_domain_ids = set(educational_domain_ids)
    educational_domains = educational_repository.get_educational_domains_from_ids(unique_educational_domain_ids)

    if len(educational_domains) < len(unique_educational_domain_ids):
        raise exceptions.EducationalDomainsNotFound()

    return educational_domains


def create_collective_offer(
    offer_data: Union[PostCollectiveOfferBodyModel, PostEducationalOfferBodyModel],
    user: User,
    offer_id: Optional[int] = None,
) -> CollectiveOffer:

    offerers_api.can_offerer_create_educational_offer(dehumanize(offer_data.offerer_id))
    venue: offerers_models.Venue = load_or_raise_error(offerers_models.Venue, offer_data.venue_id)
    check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)
    offer_validation.check_offer_subcategory_is_valid(offer_data.subcategory_id)
    offer_validation.check_offer_is_eligible_for_educational(offer_data.subcategory_id, is_educational=True)
    educational_domains = []
    if isinstance(offer_data, PostCollectiveOfferBodyModel):
        educational_domains = get_educational_domains_from_ids(offer_data.domains)
    collective_offer = educational_models.CollectiveOffer(
        venueId=venue.id,
        name=offer_data.name,
        offerId=offer_id,
        bookingEmail=offer_data.booking_email,
        description=offer_data.description,
        domains=educational_domains,
        durationMinutes=offer_data.duration_minutes,
        subcategoryId=offer_data.subcategory_id,
        students=offer_data.extra_data.students
        if isinstance(offer_data, PostEducationalOfferBodyModel)
        else offer_data.students,
        contactEmail=offer_data.extra_data.contact_email
        if isinstance(offer_data, PostEducationalOfferBodyModel)
        else offer_data.contact_email,
        contactPhone=offer_data.extra_data.contact_phone
        if isinstance(offer_data, PostEducationalOfferBodyModel)
        else offer_data.contact_phone,
        offerVenue=offer_data.extra_data.offer_venue.dict()
        if isinstance(offer_data, PostEducationalOfferBodyModel)
        else offer_data.offer_venue.dict(),
        validation=OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
    )
    db.session.add(collective_offer)
    db.session.commit()
    logger.info(
        "Collective offer template has been created",
        extra={"collectiveOfferTemplate": collective_offer.id, "offerId": offer_id},
    )
    return collective_offer


def get_collective_offer_by_id(offer_id: int) -> CollectiveOffer:
    return educational_repository.get_collective_offer_by_id(offer_id)


def get_collective_offer_template_by_id(offer_id: int) -> CollectiveOffer:
    return educational_repository.get_collective_offer_template_by_id(offer_id)


def create_collective_offer_template_from_collective_offer(
    price_detail: Optional[str], user: User, offer_id: int
) -> CollectiveOfferTemplate:
    from pcapi.core.offers.api import update_offer_fraud_information

    offer = educational_repository.get_collective_offer_by_id(offer_id)
    if offer.collectiveStock is not None:
        raise exceptions.EducationalStockAlreadyExists()

    collective_offer_template = educational_models.CollectiveOfferTemplate.create_from_collective_offer(
        offer, price_detail=price_detail
    )
    db.session.delete(offer)
    db.session.add(collective_offer_template)
    db.session.commit()

    if offer.validation == OfferValidationStatus.DRAFT:
        update_offer_fraud_information(collective_offer_template, user)

    search.unindex_collective_offer_ids([offer.id])
    search.async_index_collective_offer_template_ids([collective_offer_template.id])
    logger.info(
        "Collective offer template has been created and regular collective offer deleted",
        extra={"collectiveOfferTemplate": collective_offer_template.id, "CollectiveOffer": offer.id},
    )
    return collective_offer_template


def get_collective_offer_id_from_educational_stock(stock: Stock) -> int:
    collective_offer = educational_repository.get_collective_offer_by_offer_id(stock.offerId)
    return collective_offer.id


def edit_collective_offer_template_from_stock(stock: Stock, stock_data: dict) -> None:
    if stock_data.get("educational_price_detail") is None:
        return

    collective_offer_template = CollectiveOfferTemplate.query.filter_by(offerId=stock.offerId).one_or_none()

    if collective_offer_template is None:
        raise exceptions.CollectiveOfferTemplateNotFound()

    offer_validation.check_validation_status(collective_offer_template)

    collective_offer_template.priceDetail = stock_data["educational_price_detail"]
    db.session.add(stock)
    db.session.commit()

    logger.info(
        "Collective offer template has been updated", extra={"collective_offer_template": collective_offer_template.id}
    )

    search.async_index_collective_offer_template_ids([collective_offer_template.id])


def get_collective_offer_by_id_for_adage(offer_id: int) -> CollectiveOffer:
    return educational_repository.get_collective_offer_by_id_for_adage(offer_id)


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> CollectiveOfferTemplate:
    return educational_repository.get_collective_offer_template_by_id_for_adage(offer_id)


def transform_collective_offer_template_into_collective_offer(
    user: User, body: CollectiveStockCreationBodyModel
) -> CollectiveOffer:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(id=body.offer_id).one()

    offer_validation.check_validation_status(collective_offer_template)
    collective_offer = educational_models.CollectiveOffer.create_from_collective_offer_template(
        collective_offer_template
    )
    db.session.delete(collective_offer_template)
    db.session.add(collective_offer)
    db.session.commit()
    create_collective_stock(stock_data=body, user=user, offer_id=collective_offer.id)
    return collective_offer


def get_query_for_collective_offers_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    return educational_repository.get_query_for_collective_offers_by_ids_for_user(user=user, ids=ids)


def get_query_for_collective_offers_template_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    return educational_repository.get_query_for_collective_offers_template_by_ids_for_user(user=user, ids=ids)


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: Optional[str] = None,
    status: Optional[
        Union[
            educational_models.CollectiveBookingStatus,
            educational_models.EducationalBookingStatus,
            bookings_models.BookingStatus,
        ]
    ] = None,
) -> list[educational_models.CollectiveBooking]:
    return educational_repository.find_collective_bookings_for_adage(
        uai_code=uai_code, year_id=year_id, redactor_email=redactor_email, status=status
    )


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> Optional[educational_models.EducationalDeposit]:
    return educational_repository.find_educational_deposit_by_institution_id_and_year(
        educational_institution_id=educational_institution_id, educational_year_id=educational_year_id
    )


def get_all_educational_institutions(
    page: int, per_page_limit: int
) -> tuple[educational_models.EducationalInstitution, int]:
    offset = (per_page_limit * (page - 1)) if page > 0 else 0
    return educational_repository.get_all_educational_institutions(offset=offset, limit=per_page_limit)


def get_educational_institution_by_id(institution_id: int) -> educational_models.EducationalInstitution:
    return educational_repository.get_educational_institution_by_id(institution_id)


def update_collective_offer_educational_institution(
    offer_id: int, educational_institution_id: Optional[int], is_creating_offer: bool, user: User
) -> CollectiveOffer:
    from pcapi.core.offers.api import update_offer_fraud_information

    offer = educational_repository.get_collective_offer_by_id(offer_id)
    if educational_institution_id is not None:
        institution = get_educational_institution_by_id(educational_institution_id)
    else:
        institution = None

    if not is_creating_offer and offer.collectiveStock and not offer.collectiveStock.isEditable:
        raise exceptions.CollectiveOfferNotEditable()
    offer.institution = institution
    db.session.commit()

    if is_creating_offer and offer.validation == OfferValidationStatus.DRAFT:
        update_offer_fraud_information(offer, user)

    search.async_index_collective_offer_ids([offer_id])

    return offer


def get_collective_stock(collective_stock_id: int) -> Optional[educational_models.CollectiveStock]:
    return educational_repository.get_collective_stock(collective_stock_id)
