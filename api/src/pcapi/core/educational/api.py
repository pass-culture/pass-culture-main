import datetime
import decimal
import json
import logging
from operator import or_
from typing import Iterable
from typing import cast

from flask import current_app
from flask_sqlalchemy import BaseQuery
from pydantic import parse_obj_as
from pydantic.error_wrappers import ValidationError
import sqlalchemy as sa

from pcapi import settings
from pcapi.core import mails
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational import validation
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.exceptions import AdageException
import pcapi.core.mails.models as mails_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.core.offers import validation as offer_validation
from pcapi.core.offers.models import Stock
from pcapi.core.offers.utils import as_utc_without_timezone
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.models import User
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.adage_iframe.serialization.adage_authentication import RedactorInformation
from pcapi.routes.serialization import collective_bookings_serialize
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferBodyModel
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.utils import rest
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)
OFFERS_RECAP_LIMIT = 501


def _create_redactor(redactor_informations: RedactorInformation) -> educational_models.EducationalRedactor:
    redactor = educational_models.EducationalRedactor(
        email=redactor_informations.email,
        firstName=redactor_informations.firstname,
        lastName=redactor_informations.lastname,
        civility=redactor_informations.civility,  # type: ignore [arg-type]
    )
    repository.save(redactor)
    return redactor


def book_collective_offer(
    redactor_informations: RedactorInformation, stock_id: int
) -> educational_models.CollectiveBooking:
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
        booking = educational_models.CollectiveBooking(
            educationalInstitution=educational_institution,  # type: ignore [arg-type]
            educationalYear=educational_year,  # type: ignore [arg-type]
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
            "Coulf not notify adage of prebooking, hence send confirmation email to educational institution, as educationalBooking serialization failed.",
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
            educational_institution_id, educational_year_id  # type: ignore [arg-type]
        )
        validation.check_institution_fund(
            educational_institution_id,  # type: ignore [arg-type]
            educational_year_id,  # type: ignore [arg-type]
            collective_booking.collectiveStock.price,
            deposit,
        )
        if FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION.is_active():
            validation.check_ministry_fund(
                educational_year_id=educational_year_id,  # type: ignore [arg-type]
                booking_amount=collective_booking.collectiveStock.price,
                booking_date=collective_booking.collectiveStock.beginningDatetime,
                ministry=deposit.ministry,  # type: ignore [arg-type]
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
        data = mails_models.TransactionalEmailData(
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
        .options(sa.orm.joinedload(offerers_models.Venue.contact))
        .one()
    )
    return [venue]


def get_all_venues(page: int | None, per_page: int | None) -> list[offerers_models.Venue]:
    page = 1 if page is None else page
    per_page = 1000 if per_page is None else per_page

    return (
        offerers_models.Venue.query.filter_by(isVirtual=False)
        .order_by(offerers_models.Venue.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .options(sa.orm.joinedload(offerers_models.Venue.contact))
        .all()
    )


def get_venues_by_name(name: str) -> list[offerers_models.Venue]:
    name = name.replace(" ", "%")
    name = name.replace("-", "%")
    name = clean_accents(name)
    venues = (
        offerers_models.Venue.query.filter(
            or_(
                sa.func.unaccent(offerers_models.Venue.name).ilike(f"%{name}%"),
                sa.func.unaccent(offerers_models.Venue.publicName).ilike(f"%{name}%"),
            )
        )
        .filter(offerers_models.Venue.isVirtual.is_(False))
        .options(sa.orm.joinedload(offerers_models.Venue.contact))
        .all()
    )
    return venues


def get_educational_categories() -> dict:
    educational_subcategories = [
        subcategory for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.can_be_educational == True
    ]
    educational_categories_ids = list(set(subcategory.category.id for subcategory in educational_subcategories))
    educational_categories = [
        category for category in categories.ALL_CATEGORIES if category.id in educational_categories_ids
    ]

    return {"subcategories": educational_subcategories, "categories": educational_categories}


def notify_educational_redactor_on_collective_offer_or_stock_edit(
    collective_offer_id: int,
    updated_fields: list[str],
) -> None:
    if len(updated_fields) == 0:
        return

    active_collective_bookings = educational_repository.find_active_collective_booking_by_offer_id(collective_offer_id)
    if active_collective_bookings is None:
        return

    data = prebooking.EducationalBookingEdition(
        **prebooking.serialize_collective_booking(active_collective_bookings).dict(),
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
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
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


def _update_educational_booking_cancellation_limit_date(
    booking: educational_models.CollectiveBooking, new_beginning_datetime: datetime.datetime
) -> None:
    booking.cancellationLimitDate = educational_utils.compute_educational_booking_cancellation_limit_date(
        new_beginning_datetime, datetime.datetime.utcnow()
    )


def edit_collective_stock(
    stock: educational_models.CollectiveStock, stock_data: dict
) -> educational_models.CollectiveStock:

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

    collective_stock_unique_booking = educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.collectiveStockId == stock.id,
        sa.sql.elements.not_(
            educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.CANCELLED
        ),
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
        stock = educational_repository.get_and_lock_collective_stock(stock_id=stock.id)
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
    stock: educational_models.CollectiveStock, stock_data: dict, beginning: datetime, booking_limit_datetime: datetime  # type: ignore [valid-type]
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
    stock_data: CollectiveStockCreationBodyModel,
    user: User,
    *,
    offer_id: int | None = None,
) -> educational_models.CollectiveStock | None:
    offer_id = offer_id or stock_data.offer_id
    beginning = stock_data.beginning_datetime
    booking_limit_datetime = stock_data.booking_limit_datetime
    total_price = stock_data.total_price
    number_of_tickets = stock_data.number_of_tickets
    educational_price_detail = stock_data.educational_price_detail

    collective_offer = (
        educational_models.CollectiveOffer.query.filter_by(id=offer_id)
        .options(sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock))
        .one()
    )

    validation.check_collective_offer_number_of_collective_stocks(collective_offer)
    offer_validation.check_validation_status(collective_offer)
    if booking_limit_datetime is None:
        booking_limit_datetime = beginning

    collective_stock = educational_models.CollectiveStock(
        collectiveOffer=collective_offer,
        beginningDatetime=beginning,
        bookingLimitDatetime=booking_limit_datetime,
        price=total_price,
        numberOfTickets=number_of_tickets,
        priceDetail=educational_price_detail,
    )
    db.session.add(collective_stock)
    db.session.commit()
    logger.info(
        "Collective stock has been created",
        extra={"collective_offer": collective_offer.id, "collective_stock_id": collective_stock.id},
    )

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
    booking_period: tuple[datetime.date, datetime.date] | None = None,
    status_filter: educational_models.CollectiveBookingStatusFilter
    | None = educational_models.CollectiveBookingStatusFilter.BOOKED,
    event_date: datetime.datetime | None = None,
    venue_id: int | None = None,
    export_type: bookings_models.BookingExportType | None = bookings_models.BookingExportType.CSV,
) -> str | bytes:
    bookings_query = educational_repository.get_filtered_collective_booking_report(
        pro_user=user,
        period=booking_period,  # type: ignore [arg-type]
        status_filter=status_filter,  # type: ignore [arg-type]
        event_date=event_date,
        venue_id=venue_id,
    )

    if export_type == bookings_models.BookingExportType.EXCEL:
        return collective_bookings_serialize.serialize_collective_booking_excel_report(bookings_query)
    return collective_bookings_serialize.serialize_collective_booking_csv_report(bookings_query)


def list_collective_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    category_id: str | None,
    offerer_id: int | None,
    venue_id: int | None = None,
    name_keywords: str | None = None,
    status: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
) -> list[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate]:
    offers = educational_repository.get_collective_offers_for_filters(
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
    templates = educational_repository.get_collective_offers_template_for_filters(
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


def list_public_collective_offers(
    offerer_id: int,
    venue_id: int | None = None,
    status: offer_mixin.OfferStatus | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
    limit: int = 500,
) -> list[educational_models.CollectiveOffer]:
    return educational_repository.list_public_collective_offers(
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
        limit=limit,
    )


def get_educational_domains_from_ids(
    educational_domain_ids: list[int] | None,
) -> list[educational_models.EducationalDomain]:
    if educational_domain_ids is None:
        return []

    unique_educational_domain_ids = set(educational_domain_ids)
    educational_domains = educational_repository.get_educational_domains_from_ids(unique_educational_domain_ids)

    if len(educational_domains) < len(unique_educational_domain_ids):
        raise exceptions.EducationalDomainsNotFound()

    return educational_domains


def create_collective_offer(
    offer_data: PostCollectiveOfferBodyModel,
    user: User,
    offer_id: int | None = None,
) -> educational_models.CollectiveOffer:

    offerers_api.can_offerer_create_educational_offer(dehumanize(offer_data.offerer_id))
    venue: offerers_models.Venue = rest.load_or_raise_error(offerers_models.Venue, offer_data.venue_id)
    rest.check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)
    offer_validation.check_offer_subcategory_is_valid(offer_data.subcategory_id)
    offer_validation.check_offer_is_eligible_for_educational(offer_data.subcategory_id)
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
        students=offer_data.students,
        contactEmail=offer_data.contact_email,
        contactPhone=offer_data.contact_phone,
        offerVenue=offer_data.offer_venue.dict(),  # type: ignore [arg-type]
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=offer_data.intervention_area or [],
    )
    db.session.add(collective_offer)
    db.session.commit()
    logger.info(
        "Collective offer template has been created",
        extra={"collectiveOfferTemplate": collective_offer.id, "offerId": offer_id},
    )
    return collective_offer


def get_collective_offer_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_by_id(offer_id)


def get_collective_offer_template_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_template_by_id(offer_id)


def create_collective_offer_template_from_collective_offer(
    price_detail: str | None, user: User, offer_id: int
) -> educational_models.CollectiveOfferTemplate:
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

    if offer.validation == offer_mixin.OfferValidationStatus.DRAFT:
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


def get_collective_offer_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_by_id_for_adage(offer_id)


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOfferTemplate:
    return educational_repository.get_collective_offer_template_by_id_for_adage(offer_id)


def transform_collective_offer_template_into_collective_offer(
    user: User, body: CollectiveStockCreationBodyModel
) -> educational_models.CollectiveOffer:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(id=body.offer_id).one()
    collective_offer_template_id = collective_offer_template.id

    offer_validation.check_validation_status(collective_offer_template)
    collective_offer = educational_models.CollectiveOffer.create_from_collective_offer_template(
        collective_offer_template
    )

    db.session.delete(collective_offer_template)
    db.session.add(collective_offer)
    db.session.commit()

    search.unindex_collective_offer_template_ids([collective_offer_template_id])

    create_collective_stock(stock_data=body, user=user, offer_id=collective_offer.id)
    return collective_offer


def get_query_for_collective_offers_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    return educational_repository.get_query_for_collective_offers_by_ids_for_user(user=user, ids=ids)


def get_query_for_collective_offers_template_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    return educational_repository.get_query_for_collective_offers_template_by_ids_for_user(user=user, ids=ids)


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: str | None = None,
    status: educational_models.CollectiveBookingStatus
    | educational_models.EducationalBookingStatus
    | bookings_models.BookingStatus
    | None = None,
) -> list[educational_models.CollectiveBooking]:
    return educational_repository.find_collective_bookings_for_adage(
        uai_code=uai_code, year_id=year_id, redactor_email=redactor_email, status=status
    )


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> educational_models.EducationalDeposit | None:
    return educational_repository.find_educational_deposit_by_institution_id_and_year(
        educational_institution_id=educational_institution_id, educational_year_id=educational_year_id
    )


def get_all_educational_institutions(page: int, per_page_limit: int) -> tuple[tuple, int]:
    offset = (per_page_limit * (page - 1)) if page > 0 else 0
    return educational_repository.get_all_educational_institutions(offset=offset, limit=per_page_limit)


def search_educational_institution(
    educational_institution_id: int | None,
    name: str | None,
    institution_type: str | None,
    city: str | None,
    postal_code: str | None,
    limit: int,
) -> educational_models.EducationalInstitution:
    return educational_repository.search_educational_institution(
        educational_institution_id=educational_institution_id,
        name=name,
        city=city,
        postal_code=postal_code,
        institution_type=institution_type,
        limit=limit,
    )


def get_educational_institution_by_id(institution_id: int) -> educational_models.EducationalInstitution:
    return educational_repository.get_educational_institution_by_id(institution_id)


def update_collective_offer_educational_institution(
    offer_id: int, educational_institution_id: int | None, is_creating_offer: bool, user: User
) -> educational_models.CollectiveOffer:
    from pcapi.core.offers.api import update_offer_fraud_information

    offer = educational_repository.get_collective_offer_by_id(offer_id)
    if educational_institution_id is not None:
        institution = get_educational_institution_by_id(educational_institution_id)
    else:
        institution = None

    if not is_creating_offer and offer.collectiveStock and not offer.collectiveStock.isEditable:
        raise exceptions.CollectiveOfferNotEditable()
    offer.institution = institution  # type: ignore [assignment]
    db.session.commit()

    if is_creating_offer and offer.validation == offer_mixin.OfferValidationStatus.DRAFT:
        update_offer_fraud_information(offer, user)

    search.async_index_collective_offer_ids([offer_id])

    if educational_institution_id is not None and offer.validation == offer_mixin.OfferValidationStatus.APPROVED:
        adage_client.notify_institution_association(serialize_collective_offer(offer))

    return offer


def get_collective_stock(collective_stock_id: int) -> educational_models.CollectiveStock | None:
    return educational_repository.get_collective_stock(collective_stock_id)


def get_cultural_partners(*, force_update: bool = False) -> venues_serialize.AdageCulturalPartners:
    CULTURAL_PARTNERS_CACHE_KEY = "api:adage_cultural_partner:cache"
    CULTURAL_PARTNERS_CACHE_TIMEOUT = 24 * 60 * 60  # 24h in seconds

    redis_client = current_app.redis_client  # type: ignore [attr-defined]
    cultural_partners_json = None
    if not force_update:
        cultural_partners_json = redis_client.get(CULTURAL_PARTNERS_CACHE_KEY)

    if not cultural_partners_json:
        # update path
        adage_data = adage_client.get_cultural_partners()
        cultural_partners_raw_json = json.dumps(adage_data).encode("utf-8")
        redis_client.set(CULTURAL_PARTNERS_CACHE_KEY, cultural_partners_raw_json, ex=CULTURAL_PARTNERS_CACHE_TIMEOUT)
        cultural_partners_json = cultural_partners_raw_json.decode("utf-8")

    cultural_partners = json.loads(cultural_partners_json)
    return parse_obj_as(venues_serialize.AdageCulturalPartners, {"partners": cultural_partners})


def get_cultural_partner(siret: str) -> venues_serialize.AdageCulturalPartnerResponseModel:
    return venues_serialize.AdageCulturalPartnerResponseModel.from_orm(adage_client.get_cultural_partner(siret))


def create_collective_offer_public(
    offerer_id: int, body: public_api_collective_offers_serialize.PostCollectiveOfferBodyModel
) -> educational_models.CollectiveOffer:
    from pcapi.core.offers.api import update_offer_fraud_information

    offerers_api.can_offerer_create_educational_offer(offerer_id)
    venue = offerers_models.Venue.query.filter_by(id=body.venue_id).one_or_none()
    if venue is None or venue.managingOffererId != offerer_id:
        raise offerers_exceptions.VenueNotFoundException()
    cast(offerers_models.Venue, venue)

    offer_validation.check_offer_subcategory_is_valid(body.subcategory_id)
    offer_validation.check_offer_is_eligible_for_educational(body.subcategory_id)
    validation.check_intervention_area(body.intervention_area)

    educational_domains = educational_repository.get_educational_domains_from_names(body.domains)

    if body.educational_institution_id:
        if not educational_models.EducationalInstitution.query.filter_by(
            id=body.educational_institution_id
        ).one_or_none():
            raise exceptions.EducationalInstitutionUnknown()

    if body.offer_venue.venueId:
        query = db.session.query(sa.func.count(offerers_models.Venue.id))
        query = query.filter(
            offerers_models.Venue.id == body.offer_venue.venueId, offerers_models.Venue.managingOffererId == offerer_id
        )
        if query.scalar() == 0:
            raise offerers_exceptions.VenueNotFoundException()

    offer_venue = {
        "venueId": humanize(body.offer_venue.venueId) or "",
        "addressType": body.offer_venue.addressType,
        "otherAddress": body.offer_venue.otherAddress or "",
    }
    collective_offer = educational_models.CollectiveOffer(
        venueId=venue.id,
        name=body.name,
        description=body.description,
        subcategoryId=body.subcategory_id,
        bookingEmail=body.booking_email,
        contactEmail=body.contact_email,
        contactPhone=body.contact_phone,
        domains=educational_domains,
        durationMinutes=body.duration_minutes,
        students=body.students,
        audioDisabilityCompliant=body.audio_disability_compliant,
        mentalDisabilityCompliant=body.mental_disability_compliant,
        motorDisabilityCompliant=body.motor_disability_compliant,
        visualDisabilityCompliant=body.visual_disability_compliant,
        offerVenue=offer_venue,  # type: ignore [arg-type]
        interventionArea=body.intervention_area,
        institutionId=body.educational_institution_id,
    )

    collective_stock = educational_models.CollectiveStock(
        collectiveOffer=collective_offer,
        beginningDatetime=body.beginning_datetime,
        bookingLimitDatetime=body.booking_limit_datetime,
        price=body.total_price / 100.0,
        numberOfTickets=body.number_of_tickets,
        priceDetail=body.price_detail,
    )

    update_offer_fraud_information(offer=collective_offer, user=None)
    db.session.add(collective_offer)
    db.session.add(collective_stock)
    db.session.commit()
    search.async_index_collective_offer_ids([collective_offer.id])
    logger.info(
        "Collective offer has been created",
        extra={"offerId": collective_offer.id},
    )
    return collective_offer


def get_educational_institution_department_code(
    institution: educational_models.EducationalInstitution,
) -> str:
    department_code = PostalCode(institution.postalCode).get_departement_code()
    return department_code


def edit_collective_offer_public(
    offerer_id: int, new_values: dict, offer: educational_models.CollectiveOffer
) -> educational_models.CollectiveOffer:
    if not (offer.isEditable and offer.collectiveStock.isEditable):
        raise exceptions.CollectiveOfferNotEditable()

    offer_fields = {field for field in dir(educational_models.CollectiveOffer) if not field.startswith("_")}
    stock_fields = {field for field in dir(educational_models.CollectiveStock) if not field.startswith("_")}

    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():

        updated_fields.append(key)

        if key == "subcategoryId":
            offer_validation.check_offer_subcategory_is_valid(value)
            offer_validation.check_offer_is_eligible_for_educational(value)
            offer.subcategoryId = value
        elif key == "domains":
            domains = educational_repository.get_educational_domains_from_names(value)
            if len(domains) != len(value):
                raise exceptions.EducationalDomainsNotFound()
            offer.domains = domains
        elif key == "educationalInstitutionId":
            if value:
                if not educational_models.EducationalInstitution.query.filter_by(id=value).one_or_none():
                    raise exceptions.EducationalInstitutionUnknown()
            offer.institutionId = value
        elif key == "offerVenue":
            offer.offerVenue["venueId"] = humanize(value["venueId"]) or ""
            offer.offerVenue["addressType"] = value["addressType"].value
            offer.offerVenue["otherAddress"] = value["otherAddress"] or ""
        elif key == "bookingLimitDatetime" and value is None:
            offer.collectiveStock.bookingLimitDatetime = new_values.get(
                "beginningDatetime", offer.collectiveStock.beginningDatetime
            )
        elif key in stock_fields:
            setattr(offer.collectiveStock, key, value)
        elif key in offer_fields:
            setattr(offer, key, value)
        else:
            raise ValueError(f"unknown field {key}")

    db.session.commit()

    search.async_index_collective_offer_ids([offer.id])

    notify_educational_redactor_on_collective_offer_or_stock_edit(
        offer.id,
        updated_fields,
    )
    return offer


def synchronize_adage_ids_on_venues() -> None:
    adage_cultural_partners = get_cultural_partners(force_update=True)

    filtered_cultural_partner_by_ids = {}
    for cultural_partner in adage_cultural_partners.partners:
        if cultural_partner.venueId is not None and cultural_partner.synchroPass:
            filtered_cultural_partner_by_ids[cultural_partner.venueId] = cultural_partner

    venues: list[offerers_models.Venue] = offerers_models.Venue.query.filter(
        offerers_models.Venue.id.in_(filtered_cultural_partner_by_ids.keys())
    ).all()

    for venue in venues:
        if not venue.adageId:
            # Update the users in SiB in case of previous adageId being none
            # This is because we track if the user has an adageId, not the value of the adageId
            emails = get_emails_by_venue(venue)
            for email in emails:
                update_external_pro(email)

        venue.adageId = str(filtered_cultural_partner_by_ids[venue.id].id)

    db.session.commit()
