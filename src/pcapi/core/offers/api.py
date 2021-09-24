import datetime
import logging
from typing import Optional
from typing import Union

from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
import pytz
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import func
import yaml
from yaml.scanner import ScannerError

from pcapi import settings
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import remove_thumb
from pcapi.core import search
from pcapi.core.bookings.api import cancel_bookings_when_offerer_deletes_stock
from pcapi.core.bookings.api import mark_as_unused
from pcapi.core.bookings.api import update_cancellation_limit_dates
from pcapi.core.bookings.conf import get_limit_configuration_for_type_and_version
from pcapi.core.bookings.models import Booking
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.categories import subcategories
from pcapi.core.categories.conf import can_create_from_isbn
from pcapi.core.offers.exceptions import OfferAlreadyReportedError
from pcapi.core.offers.exceptions import ReportMalformed
from pcapi.core.offers.exceptions import WrongFormatInFraudConfigurationFile
from pcapi.core.offers.models import OfferReport
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
from pcapi.core.offers.offer_validation import compute_offer_validation_score
from pcapi.core.offers.offer_validation import parse_offer_validation_config
import pcapi.core.offers.repository as offers_repository
from pcapi.core.offers.validation import KEY_VALIDATION_CONFIG
from pcapi.core.offers.validation import check_validation_config_parameters
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import User
from pcapi.domain import admin_emails
from pcapi.domain import offer_report_emails
from pcapi.domain import user_emails
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.models import Criterion
from pcapi.models import Offer
from pcapi.models import OfferCriterion
from pcapi.models import Product
from pcapi.models import Venue
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.deposit import DepositType
from pcapi.models.feature import FeatureToggle
from pcapi.repository import offer_queries
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.serialization.offers_serialize import PostOfferBodyModel
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.utils import mailing
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_raise_error
from pcapi.workers.push_notification_job import send_cancel_booking_notification

from . import validation
from .exceptions import ThumbnailStorageError
from .models import ActivationCode
from .models import Mediation


logger = logging.getLogger(__name__)


OFFERS_RECAP_LIMIT = 201
UNCHANGED = object()
VALIDATION_KEYWORDS_MAPPING = {
    "APPROVED": OfferValidationStatus.APPROVED,
    "PENDING": OfferValidationStatus.PENDING,
    "REJECTED": OfferValidationStatus.REJECTED,
}


def list_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    category_id: Optional[str],
    offerer_id: Optional[int],
    venue_id: Optional[int] = None,
    name_keywords_or_isbn: Optional[str] = None,
    status: Optional[str] = None,
    creation_mode: Optional[str] = None,
    period_beginning_date: Optional[str] = None,
    period_ending_date: Optional[str] = None,
) -> OffersRecap:
    return offers_repository.get_capped_offers_for_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offers_limit=OFFERS_RECAP_LIMIT,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords_or_isbn=name_keywords_or_isbn,
        creation_mode=creation_mode,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
    )


def create_offer(offer_data: PostOfferBodyModel, user: User) -> Offer:
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(offer_data.subcategory_id)
    venue = load_or_raise_error(Venue, offer_data.venue_id)
    check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)
    if offer_data.product_id:
        product = load_or_raise_error(Product, offer_data.product_id)
        product_subcategory = subcategories.ALL_SUBCATEGORIES_DICT[product.subcategoryId]
        offer = Offer(
            product=product,
            type=product_subcategory.matching_type,  # FIXME: fseguin(2021-07-22): deprecated
            subcategoryId=product.subcategoryId,
            name=product.name,
            description=product.description,
            url=product.url,
            mediaUrls=product.mediaUrls,
            conditions=product.conditions,
            ageMin=product.ageMin,
            ageMax=product.ageMax,
            durationMinutes=product.durationMinutes,
            isNational=product.isNational,
            extraData=product.extraData,
        )
    elif FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION.is_active() and can_create_from_isbn(
        subcategory_id=subcategory.id if subcategory else None, offer_type=subcategory.matching_type
    ):
        product = _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(offer_data.extra_data["isbn"])
        product_subcategory = subcategories.ALL_SUBCATEGORIES_DICT[product.subcategoryId]
        extra_data = product.extraData
        extra_data.update(offer_data.extra_data)
        offer = Offer(
            product=product,
            type=product_subcategory.matching_type,  # FIXME: fseguin(2021-07-22): deprecated
            subcategoryId=product.subcategoryId,
            name=offer_data.name,
            description=offer_data.description if offer_data.description else product.description,
            url=offer_data.url if offer_data.url else product.url,
            mediaUrls=offer_data.url if offer_data.url else product.url,
            conditions=offer_data.conditions if offer_data.conditions else product.conditions,
            ageMin=offer_data.age_min if offer_data.age_min else product.ageMin,
            ageMax=offer_data.age_max if offer_data.age_max else product.ageMax,
            isNational=offer_data.is_national if offer_data.is_national else product.isNational,
            extraData=extra_data,
        )
    else:
        data = offer_data.dict(by_alias=True)
        data["type"] = subcategory.matching_type  # FIXME: fseguin(2021-07-22): deprecated
        product = Product()
        if data.get("url"):
            data["isNational"] = True
        product.populate_from_dict(data)
        offer = Offer()
        offer.populate_from_dict(data)
        offer.product = product
        offer.subcategoryId = subcategory.id if subcategory else None
        offer.type = subcategory.matching_type
        offer.product.owningOfferer = venue.managingOfferer

    offer.venue = venue
    offer.bookingEmail = offer_data.booking_email
    offer.externalTicketOfficeUrl = offer_data.external_ticket_office_url
    offer.audioDisabilityCompliant = offer_data.audio_disability_compliant
    offer.mentalDisabilityCompliant = offer_data.mental_disability_compliant
    offer.motorDisabilityCompliant = offer_data.motor_disability_compliant
    offer.visualDisabilityCompliant = offer_data.visual_disability_compliant
    offer.isEducational = offer_data.is_educational
    offer.validation = OfferValidationStatus.DRAFT

    repository.save(offer)
    logger.info("Offer has been created", extra={"offer": offer.id, "venue": venue.id, "product": offer.productId})

    return offer


def update_offer(
    offer: Offer,
    bookingEmail: str = UNCHANGED,
    description: str = UNCHANGED,
    isNational: bool = UNCHANGED,
    name: str = UNCHANGED,
    extraData: dict = UNCHANGED,
    externalTicketOfficeUrl: str = UNCHANGED,
    url: str = UNCHANGED,
    withdrawalDetails: str = UNCHANGED,
    isActive: bool = UNCHANGED,
    isDuo: bool = UNCHANGED,
    durationMinutes: int = UNCHANGED,
    mediaUrls: list[str] = UNCHANGED,
    ageMin: int = UNCHANGED,
    ageMax: int = UNCHANGED,
    conditions: str = UNCHANGED,
    venueId: str = UNCHANGED,
    productId: str = UNCHANGED,
    audioDisabilityCompliant: bool = UNCHANGED,
    mentalDisabilityCompliant: bool = UNCHANGED,
    motorDisabilityCompliant: bool = UNCHANGED,
    visualDisabilityCompliant: bool = UNCHANGED,
) -> Offer:
    validation.check_validation_status(offer)
    # fmt: off
    modifications = {
        field: new_value
        for field, new_value in locals().items()
        if field != 'offer'
        and new_value is not UNCHANGED  # has the user provided a value for this field
        and getattr(offer, field) != new_value  # is the value different from what we have on database?
    }
    # fmt: on
    if not modifications:
        return offer

    if offer.isFromProvider:
        validation.check_update_only_allowed_fields_for_offer_from_provider(set(modifications), offer.lastProvider)

    offer.populate_from_dict(modifications)
    if offer.product.owningOfferer and offer.product.owningOfferer == offer.venue.managingOfferer:
        offer.product.populate_from_dict(modifications)
        product_has_been_updated = True
    else:
        product_has_been_updated = False

    if offer.isFromAllocine:
        offer.fieldsUpdated = list(set(offer.fieldsUpdated) | set(modifications))

    repository.save(offer)
    logger.info("Offer has been updated", extra={"offer": offer.id})
    if product_has_been_updated:
        repository.save(offer.product)
        logger.info("Product has been updated", extra={"product": offer.product.id})

    search.async_index_offer_ids([offer.id])

    return offer


def batch_update_offers(query, update_fields):
    offer_ids_tuples = query.filter(Offer.validation == OfferValidationStatus.APPROVED).with_entities(Offer.id)

    offer_ids = [offer_id for offer_id, in offer_ids_tuples]
    number_of_offers_to_update = len(offer_ids)
    batch_size = 1000
    for current_start_index in range(0, number_of_offers_to_update, batch_size):
        offer_ids_batch = offer_ids[
            current_start_index : min(current_start_index + batch_size, number_of_offers_to_update)
        ]

        query_to_update = Offer.query.filter(Offer.id.in_(offer_ids_batch))
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.commit()

        search.async_index_offer_ids(offer_ids_batch)


def _create_stock(
    offer: Offer,
    price: float,
    quantity: int = None,
    beginning: datetime.datetime = None,
    booking_limit_datetime: datetime.datetime = None,
) -> Stock:
    validation.check_required_dates_for_stock(offer, beginning, booking_limit_datetime)
    validation.check_stock_can_be_created_for_offer(offer)
    validation.check_stock_price(price, offer.isEvent)
    validation.check_stock_quantity(quantity)

    return Stock(
        offer=offer,
        price=price,
        quantity=quantity,
        beginningDatetime=beginning,
        bookingLimitDatetime=booking_limit_datetime,
    )


def _edit_stock(
    stock: Stock,
    price: float,
    quantity: int,
    beginning: datetime.datetime,
    booking_limit_datetime: datetime.datetime,
) -> Stock:
    # FIXME (dbaty, 2020-11-25): We need this ugly workaround because
    # the frontend sends us datetimes like "2020-12-03T14:00:00Z"
    # (note the "Z" suffix). Pydantic deserializes it as a datetime
    # *with* a timezone. However, datetimes are stored in the database
    # as UTC datetimes *without* any timezone. Thus, we wrongly detect
    # a change for the "beginningDatetime" field for Allocine stocks:
    # because we do not allow it to be changed, we raise an error when
    # we should not.
    def as_utc_without_timezone(d: datetime.datetime) -> datetime.datetime:
        return d.astimezone(pytz.utc).replace(tzinfo=None)

    if beginning:
        beginning = as_utc_without_timezone(beginning)
    if booking_limit_datetime:
        booking_limit_datetime = as_utc_without_timezone(booking_limit_datetime)

    validation.check_stock_is_updatable(stock)
    validation.check_required_dates_for_stock(stock.offer, beginning, booking_limit_datetime)
    validation.check_stock_price(price, stock.offer.isEvent)
    validation.check_stock_quantity(quantity, stock.dnBookedQuantity)
    validation.check_activation_codes_expiration_datetime_on_stock_edition(
        stock.activationCodes,
        booking_limit_datetime,
    )

    updates = {
        "price": price,
        "quantity": quantity,
        "beginningDatetime": beginning,
        "bookingLimitDatetime": booking_limit_datetime,
    }

    # fmt: off
    updated_fields = {
        attr
        for attr, new_value in updates.items()
        if new_value != getattr(stock, attr)
    }
    # fmt: on
    if "price" in updated_fields:
        validation.check_stock_has_no_custom_reimbursement_rule(stock)
    if stock.offer.isFromAllocine:
        validation.check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields)
        stock.fieldsUpdated = list(updated_fields)

    for model_attr, value in updates.items():
        setattr(stock, model_attr, value)

    return stock


def _notify_beneficiaries_upon_stock_edit(stock: Stock):
    bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
    if bookings:
        bookings = update_cancellation_limit_dates(bookings, stock.beginningDatetime)
        date_in_two_days = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        check_event_is_in_more_than_48_hours = stock.beginningDatetime > date_in_two_days
        if check_event_is_in_more_than_48_hours:
            bookings = _invalidate_bookings(bookings)
        try:
            user_emails.send_batch_stock_postponement_emails_to_users(bookings)
        except mailing.MailServiceException as exc:
            # fmt: off
            logger.exception(
                "Could not notify beneficiaries about update of stock",
                extra={
                    "exc": str(exc),
                    "stock": stock.id,
                }
            )
            # fmt: on


def upsert_stocks(
    offer_id: int, stock_data_list: list[Union[StockCreationBodyModel, StockEditionBodyModel]], user: User
) -> list[Stock]:
    activation_codes = []
    stocks = []
    edited_stocks = []
    edited_stocks_previous_beginnings = {}

    offer = offer_queries.get_offer_by_id(offer_id)

    for stock_data in stock_data_list:
        if isinstance(stock_data, StockEditionBodyModel):
            stock = (
                Stock.queryNotSoftDeleted()
                .filter_by(id=stock_data.id)
                .options(joinedload(Stock.activationCodes))
                .first_or_404()
            )
            if stock.offerId != offer_id:
                errors = ApiErrors()
                errors.add_error(
                    "global", "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
                )
                errors.status_code = 403
                raise errors
            edited_stocks_previous_beginnings[stock.id] = stock.beginningDatetime
            edited_stock = _edit_stock(
                stock,
                price=stock_data.price,
                quantity=stock_data.quantity,
                beginning=stock_data.beginning_datetime,
                booking_limit_datetime=stock_data.booking_limit_datetime,
            )
            edited_stocks.append(edited_stock)
            stocks.append(edited_stock)
        else:
            activation_codes_exist = stock_data.activation_codes is not None and len(stock_data.activation_codes) > 0  # type: ignore[arg-type]

            if activation_codes_exist:
                validation.check_offer_is_digital(offer)
                validation.check_activation_codes_expiration_datetime(
                    stock_data.activation_codes_expiration_datetime,
                    stock_data.booking_limit_datetime,
                )

            quantity = len(stock_data.activation_codes) if activation_codes_exist else stock_data.quantity  # type: ignore[arg-type]

            created_stock = _create_stock(
                offer=offer,
                price=stock_data.price,
                quantity=quantity,
                beginning=stock_data.beginning_datetime,
                booking_limit_datetime=stock_data.booking_limit_datetime,
            )

            if activation_codes_exist:
                for activation_code in stock_data.activation_codes:  # type: ignore[union-attr]
                    activation_codes.append(
                        ActivationCode(
                            code=activation_code,
                            expirationDate=stock_data.activation_codes_expiration_datetime,
                            stock=created_stock,
                        )
                    )

            stocks.append(created_stock)

    repository.save(*stocks, *activation_codes)
    logger.info("Stock has been created or updated", extra={"offer": offer_id})

    if offer.validation == OfferValidationStatus.DRAFT:
        offer.validation = set_offer_status_based_on_fraud_criteria(offer)
        offer.author = user
        offer.lastValidationDate = datetime.datetime.utcnow()
        if offer.validation == OfferValidationStatus.PENDING or offer.validation == OfferValidationStatus.REJECTED:
            offer.isActive = False
        repository.save(offer)
        if offer.validation == OfferValidationStatus.APPROVED:
            admin_emails.send_offer_creation_notification_to_administration(offer)

    for stock in edited_stocks:
        previous_beginning = edited_stocks_previous_beginnings[stock.id]
        if stock.beginningDatetime != previous_beginning:
            _notify_beneficiaries_upon_stock_edit(stock)
    search.async_index_offer_ids([offer.id])

    return stocks


def _invalidate_bookings(bookings: list[Booking]) -> list[Booking]:
    for booking in bookings:
        if booking.isUsed:
            mark_as_unused(booking)
    return bookings


def delete_stock(stock: Stock) -> None:
    validation.check_stock_is_deletable(stock)

    stock.isSoftDeleted = True
    repository.save(stock)

    # the algolia sync for the stock will happen within this function
    cancelled_bookings = cancel_bookings_when_offerer_deletes_stock(stock)

    logger.info(
        "Deleted stock and cancelled its bookings",
        extra={"stock": stock.id, "bookings": [b.id for b in cancelled_bookings]},
    )
    if cancelled_bookings:
        for booking in cancelled_bookings:
            try:
                user_emails.send_warning_to_user_after_pro_booking_cancellation(booking)
            except mailing.MailServiceException as exc:
                logger.exception(
                    "Could not notify beneficiary about deletion of stock",
                    extra={
                        "exc": str(exc),
                        "stock": stock.id,
                        "booking": booking.id,
                    },
                )
        try:
            user_emails.send_offerer_bookings_recap_email_after_offerer_cancellation(cancelled_bookings)
        except mailing.MailServiceException as exc:
            logger.exception(
                "Could not notify offerer about deletion of stock",
                extra={
                    "exc": str(exc),
                    "stock": stock.id,
                },
            )

        send_cancel_booking_notification.delay([booking.id for booking in cancelled_bookings])


def create_mediation(
    user: User,
    offer: Offer,
    credit: str,
    image_as_bytes: bytes,
    crop_params: tuple = None,
) -> Mediation:
    # checks image type, min dimensions
    validation.check_image(image_as_bytes)

    mediation = Mediation(
        author=user,
        offer=offer,
        credit=credit,
    )
    # `create_thumb()` requires the object to have an id, so we must save now.
    repository.save(mediation)

    try:
        create_thumb(mediation, image_as_bytes, image_index=0, crop_params=crop_params)

    except Exception as exc:
        logger.exception("An unexpected error was encountered during the thumbnail creation: %s", exc)
        # I could not use savepoints and rollbacks with SQLA
        repository.delete(mediation)
        raise ThumbnailStorageError

    else:
        mediation.thumbCount = 1
        repository.save(mediation)
        # cleanup former thumbnails and mediations

        previous_mediations = (
            Mediation.query.filter(Mediation.offerId == offer.id).filter(Mediation.id != mediation.id).all()
        )
        for previous_mediation in previous_mediations:
            try:
                for thumb_index in range(0, previous_mediation.thumbCount):
                    remove_thumb(previous_mediation, image_index=thumb_index)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "An unexpected error was encountered during the thumbnails deletion for %s: %s",
                    mediation,
                    exc,
                )
            else:
                repository.delete(previous_mediation)

        search.async_index_offer_ids([offer.id])

        return mediation


def update_offer_and_stock_id_at_providers(venue: Venue, old_siret: str) -> None:
    current_siret = venue.siret

    offer_ids = (
        Offer.query.filter(Offer.venueId == venue.id)
        .filter(Offer.idAtProviders.endswith(old_siret))
        .with_entities(Offer.id)
        .all()
    )
    stock_ids = (
        Stock.query.join(Offer)
        .filter(Offer.venueId == venue.id)
        .filter(Stock.idAtProviders.endswith(old_siret))
        .with_entities(Stock.id)
        .all()
    )

    batch_size = 100

    for offer_index in range(0, len(offer_ids), batch_size):
        Offer.query.filter(Offer.id.in_(offer_ids[offer_index : offer_index + batch_size])).update(
            {Offer.idAtProviders: func.replace(Offer.idAtProviders, old_siret, current_siret)},
            synchronize_session=False,
        )
        db.session.commit()
        offer_index = offer_index + batch_size

    for stock_index in range(0, len(stock_ids), batch_size):
        Stock.query.filter(Stock.id.in_(stock_ids[stock_index : stock_index + batch_size])).update(
            {Stock.idAtProviders: func.replace(Stock.idAtProviders, old_siret, current_siret)},
            synchronize_session=False,
        )
        db.session.commit()
        stock_index = stock_index + batch_size


def get_expense_domains(offer: Offer) -> list[ExpenseDomain]:
    # TODO(venaud, 08-09-2021): Deposits type GRANT_15, GRANT_16 and GRANT_17 does not have caps, so this hack works.
    #  It will need to be adapted (and the frontend updated) if others types or versions change that (or for a better implementation)
    domains = {ExpenseDomain.ALL.value}

    grant_18_versions = [1, 2]
    for grant_18_version in grant_18_versions:
        configuration = get_limit_configuration_for_type_and_version(DepositType.GRANT_18, grant_18_version)
        if configuration.digital_cap_applies(offer):
            domains.add(ExpenseDomain.DIGITAL.value)
        if configuration.physical_cap_applies(offer):
            domains.add(ExpenseDomain.PHYSICAL.value)

    return list(domains)


def add_criteria_to_offers(criteria: list[Criterion], isbn: Optional[str] = None, visa: Optional[str] = None) -> bool:
    if not isbn and not visa:
        return False

    query = Product.query
    if isbn:
        isbn = isbn.replace("-", "").replace(" ", "")
        query = query.filter(Product.extraData["isbn"].astext == isbn)
    if visa:
        query = query.filter(Product.extraData["visa"].astext == visa)

    products = query.all()
    if not products:
        return False

    offer_ids_query = Offer.query.filter(
        Offer.productId.in_(p.id for p in products), Offer.isActive.is_(True)
    ).with_entities(Offer.id)
    offer_ids = [offer_id for offer_id, in offer_ids_query.all()]

    if not offer_ids:
        return False

    offer_criteria: list[OfferCriterion] = []
    for criterion in criteria:
        logger.info("Adding criterion %s to %d offers", criterion, len(offer_ids))

        offer_criteria.extend(OfferCriterion(offerId=offer_id, criterionId=criterion.id) for offer_id in offer_ids)

    db.session.bulk_save_objects(offer_criteria)
    db.session.commit()

    search.async_index_offer_ids(offer_ids)

    return True


def deactivate_inappropriate_products(isbn: str) -> bool:
    products = Product.query.filter(Product.extraData["isbn"].astext == isbn).all()
    if not products:
        return False

    for product in products:
        product.isGcuCompatible = False
        db.session.add(product)

    offers = Offer.query.filter(Offer.productId.in_(p.id for p in products)).filter(Offer.isActive.is_(True))
    offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id).all()]
    offers.update(values={"isActive": False}, synchronize_session="fetch")

    try:
        db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark product and offers as inappropriate: %s",
            extra={"isbn": isbn, "products": [p.id for p in products], "exc": str(exception)},
        )
        return False
    logger.info(
        "Deactivated inappropriate products",
        extra={"isbn": isbn, "products": [p.id for p in products], "offers": offer_ids},
    )

    search.async_index_offer_ids(offer_ids)

    return True


def set_offer_status_based_on_fraud_criteria(offer: Offer) -> OfferValidationStatus:
    # TODO (rchaffal) to delete after implementation is completed
    if not settings.IS_PROD and FeatureToggle.OFFER_VALIDATION_MOCK_COMPUTATION.is_active():
        for keyword, validation_status in VALIDATION_KEYWORDS_MAPPING.items():
            if keyword in offer.name:
                return validation_status

    current_config = offers_repository.get_current_offer_validation_config()
    if not current_config:
        return OfferValidationStatus.APPROVED

    minimum_score, validation_rules = parse_offer_validation_config(offer, current_config)

    score = compute_offer_validation_score(validation_rules)
    if score < minimum_score:
        status = OfferValidationStatus.PENDING
    else:
        status = OfferValidationStatus.APPROVED

    logger.info("Computed offer validation", extra={"offer": offer.id, "score": score, "status": status.value})
    return status


def update_pending_offer_validation(offer: Offer, validation_status: OfferValidationStatus) -> bool:
    offer = offer_queries.get_offer_by_id(offer.id)
    if offer.validation != OfferValidationStatus.PENDING:
        logger.info(
            "Offer validation status cannot be updated, initial validation status is not PENDING. %s",
            extra={"offer": offer.id},
        )
        return False
    offer.validation = validation_status
    if validation_status == OfferValidationStatus.APPROVED:
        offer.isActive = True

    try:
        db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not update offer validation status: %s",
            extra={"offer": offer.id, "validation_status": validation_status, "exc": str(exception)},
        )
        return False
    search.async_index_offer_ids([offer.id])
    logger.info("Offer validation status updated", extra={"offer": offer.id})
    return True


def import_offer_validation_config(config_as_yaml: str, user: User = None) -> OfferValidationConfig:
    try:
        config_as_dict = yaml.safe_load(config_as_yaml)
        check_validation_config_parameters(config_as_dict, KEY_VALIDATION_CONFIG["init"])
    except (KeyError, ValueError, ScannerError) as error:
        logger.exception(
            "Wrong configuration file format: %s",
            error,
            extra={"exc": str(error)},
        )
        raise WrongFormatInFraudConfigurationFile(str(error))

    config = OfferValidationConfig(specs=config_as_dict, user=user)
    repository.save(config)
    return config


def _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(isbn: str) -> Product:
    product = Product.query.filter(Product.extraData["isbn"].astext == isbn).first()
    if product is None or not product.isGcuCompatible:
        errors = ApiErrors()
        errors.add_error(
            "isbn",
            "Ce produit n’est pas éligible au pass Culture.",
        )
        errors.status_code = 400
        raise errors
    return product


def unindex_expired_offers(process_all_expired: bool = False):
    """Unindex offers that have expired.

    By default, process offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included).

    If ``process_all_expired`` is true, process... well all expired
    offers.
    """
    start_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    interval = [start_of_day - datetime.timedelta(days=2), start_of_day]
    if process_all_expired:
        interval[0] = datetime.datetime(2000, 1, 1)  # arbitrary old date

    page = 0
    limit = settings.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE
    while True:
        offers = offers_repository.get_expired_offers(interval)
        offers = offers.offset(page * limit).limit(limit)
        offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id)]

        if not offer_ids:
            break

        logger.info("[ALGOLIA] Found %d expired offers to unindex", len(offer_ids))
        search.unindex_offer_ids(offer_ids)
        page += 1


def is_activation_code_applicable(stock: Stock):
    return (
        stock.canHaveActivationCodes
        and FeatureToggle.ENABLE_ACTIVATION_CODES.is_active()
        and db.session.query(ActivationCode.query.filter_by(stock=stock).exists()).scalar()
    )


def report_offer(user: User, offer: Offer, reason: str, custom_reason: Optional[str]) -> None:
    try:
        # transaction() handles the commit/rollback operations
        #
        # UNIQUE_VIOLATION, CHECK_VIOLATION and STRING_DATA_RIGHT_TRUNCATION
        # errors are specific ones:
        # either the user tried to report the same error twice, which is not
        # allowed, or the client sent a invalid report (eg. OTHER without
        # custom reason / custom reason too long).
        #
        # Other errors are unexpected and are therefore re-raised as is.
        with transaction():
            report = OfferReport(user=user, offer=offer, reason=reason, customReasonContent=custom_reason)
            db.session.add(report)
    except exc.IntegrityError as error:
        if error.orig.pgcode == UNIQUE_VIOLATION:
            raise OfferAlreadyReportedError() from error
        if error.orig.pgcode == CHECK_VIOLATION:
            raise ReportMalformed() from error
        raise

    offer_report_emails.send_report_notification(user, offer, reason, custom_reason)
