import copy
import datetime
import logging
from typing import List
from typing import Optional
from typing import Union

from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
from pydantic import ValidationError
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
import yaml
from yaml.scanner import ScannerError

from pcapi import settings
from pcapi.connectors.api_adage import AdageException
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import remove_thumb
from pcapi.core import search
from pcapi.core.bookings.api import cancel_bookings_from_stock_by_offerer
from pcapi.core.bookings.api import mark_as_unused
from pcapi.core.bookings.api import update_cancellation_limit_dates
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.categories import subcategories
from pcapi.core.categories.conf import can_create_from_isbn
from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.adage_backends as adage_client
from pcapi.core.educational.utils import compute_educational_booking_cancellation_limit_date
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_pro_to_beneficiary import (
    send_booking_cancellation_by_pro_to_beneficiary_email,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_confirmation_by_pro import (
    send_booking_cancellation_confirmation_by_pro_email,
)
from pcapi.core.mails.transactional.bookings.booking_postponed_by_pro_to_beneficiary import (
    send_batch_booking_postponement_email_to_users,
)
from pcapi.core.mails.transactional.pro.event_offer_postponed_confirmation_to_pro import (
    send_event_offer_postponement_confirmation_email_to_pro,
)
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation
from pcapi.core.offers.exceptions import OfferAlreadyReportedError
from pcapi.core.offers.exceptions import ReportMalformed
from pcapi.core.offers.exceptions import WrongFormatInFraudConfigurationFile
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferReport
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
from pcapi.core.offers.offer_validation import compute_offer_validation_score
from pcapi.core.offers.offer_validation import parse_offer_validation_config
import pcapi.core.offers.repository as offers_repository
from pcapi.core.offers.utils import as_utc_without_timezone
from pcapi.core.offers.validation import KEY_VALIDATION_CONFIG
from pcapi.core.offers.validation import check_offer_is_eligible_for_educational
from pcapi.core.offers.validation import check_offer_not_duo_and_educational
from pcapi.core.offers.validation import check_offer_subcategory_is_valid
from pcapi.core.offers.validation import check_shadow_stock_is_editable
from pcapi.core.offers.validation import check_validation_config_parameters
from pcapi.core.payments import conf as deposit_conf
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import User
from pcapi.domain import admin_emails
from pcapi.domain import offer_report_emails
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.criterion import Criterion
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.product import Product
from pcapi.repository import offer_queries
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking
from pcapi.routes.serialization.offers_serialize import CompletedEducationalOfferModel
from pcapi.routes.serialization.offers_serialize import EducationalOfferShadowStockBodyModel
from pcapi.routes.serialization.offers_serialize import PostEducationalOfferBodyModel
from pcapi.routes.serialization.offers_serialize import PostOfferBodyModel
from pcapi.routes.serialization.stock_serialize import EducationalStockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_raise_error
from pcapi.workers.push_notification_job import send_cancel_booking_notification

from .exceptions import ThumbnailStorageError
from .models import ActivationCode
from .models import Mediation


logger = logging.getLogger(__name__)


OFFERS_RECAP_LIMIT = 501
UNCHANGED = object()


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


def create_educational_offer(offer_data: PostEducationalOfferBodyModel, user: User) -> Offer:
    offerers_api.can_offerer_create_educational_offer(dehumanize(offer_data.offerer_id))
    completed_data = CompletedEducationalOfferModel(**offer_data.dict(by_alias=True))
    offer = create_offer(completed_data, user)
    create_collective_offer(offer)
    return offer


def create_collective_offer(
    offer: Offer,
) -> None:
    collective_offer = educational_models.CollectiveOffer.create_from_offer(offer)
    db.session.add(collective_offer)
    db.session.commit()
    logger.info(
        "Collective offer template has been created",
        extra={"collectiveOfferTemplate": collective_offer.id, "offerId": offer.id},
    )


def create_offer(
    offer_data: Union[PostOfferBodyModel, CompletedEducationalOfferModel],
    user: User,
) -> Offer:
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(offer_data.subcategory_id)
    venue = load_or_raise_error(Venue, offer_data.venue_id)
    check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)
    _check_offer_data_is_valid(offer_data)
    if _is_able_to_create_book_offer_from_isbn(subcategory):
        offer = _initialize_book_offer_from_template(offer_data)
    else:
        offer = _initialize_offer_with_new_data(offer_data, subcategory, venue)

    _complete_common_offer_fields(offer, offer_data, venue)

    repository.save(offer)
    logger.info("Offer has been created", extra={"offer": offer.id, "venue": venue.id, "product": offer.productId})

    update_external_pro(venue.bookingEmail)

    return offer


def _is_able_to_create_book_offer_from_isbn(subcategory: subcategories.Subcategory) -> bool:
    return FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION.is_active() and can_create_from_isbn(
        subcategory_id=subcategory.id
    )


def _initialize_book_offer_from_template(
    offer_data: Union[PostOfferBodyModel, CompletedEducationalOfferModel]
) -> Offer:
    product = _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(offer_data.extra_data["isbn"])
    extra_data = product.extraData
    extra_data.update(offer_data.extra_data)
    offer = Offer(
        product=product,
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
    return offer


def _initialize_offer_with_new_data(
    offer_data: Union[PostOfferBodyModel, CompletedEducationalOfferModel],
    subcategory: subcategories.Subcategory,
    venue: Venue,
) -> Offer:
    data = offer_data.dict(by_alias=True)
    product = Product()
    if data.get("url"):
        data["isNational"] = True
    product.populate_from_dict(data)
    offer = Offer()
    offer.populate_from_dict(data)
    offer.product = product
    offer.subcategoryId = subcategory.id if subcategory else None
    offer.product.owningOfferer = venue.managingOfferer
    return offer


def _complete_common_offer_fields(
    offer: Offer,
    offer_data: Union[PostOfferBodyModel, CompletedEducationalOfferModel],
    venue: Venue,
) -> None:
    offer.venue = venue
    offer.bookingEmail = offer_data.booking_email
    offer.externalTicketOfficeUrl = offer_data.external_ticket_office_url
    offer.audioDisabilityCompliant = offer_data.audio_disability_compliant
    offer.mentalDisabilityCompliant = offer_data.mental_disability_compliant
    offer.motorDisabilityCompliant = offer_data.motor_disability_compliant
    offer.visualDisabilityCompliant = offer_data.visual_disability_compliant
    offer.validation = OfferValidationStatus.DRAFT
    offer.isEducational = offer_data.is_educational


def _check_offer_data_is_valid(
    offer_data: Union[PostOfferBodyModel, CompletedEducationalOfferModel],
) -> None:
    # FIXME(cgaunet, 2021-11-24): remove this check once educational choice is removed
    # from individual offer creation route
    check_offer_not_duo_and_educational(offer_data.is_duo, offer_data.is_educational)
    check_offer_is_eligible_for_educational(offer_data.subcategory_id, offer_data.is_educational)
    check_offer_subcategory_is_valid(offer_data.subcategory_id)


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


def update_educational_offer(
    offer: Offer,
    new_values: dict,
) -> Offer:
    validation.check_validation_status(offer)
    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():
        if key == "extraData":
            extra_data = copy.deepcopy(offer.extraData)

            for extra_data_key, extra_data_value in value.items():
                # We denormalize extra_data for Adage mailing
                updated_fields.append(extra_data_key)
                extra_data[extra_data_key] = extra_data_value

            offer.extraData = extra_data
            continue

        updated_fields.append(key)

        if key == "subcategoryId":
            validation.check_offer_is_eligible_for_educational(value.name, True)
            offer.subcategoryId = value.name
            continue

        setattr(offer, key, value)

    repository.save(offer)

    search.async_index_offer_ids([offer.id])

    educational_api.notify_educational_redactor_on_educational_offer_or_stock_edit(
        offer.id,
        updated_fields,
    )


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
    validation.check_stock_price(price, offer)
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

    if beginning:
        beginning = as_utc_without_timezone(beginning)
    if booking_limit_datetime:
        booking_limit_datetime = as_utc_without_timezone(booking_limit_datetime)

    validation.check_stock_is_updatable(stock)
    validation.check_required_dates_for_stock(stock.offer, beginning, booking_limit_datetime)
    validation.check_stock_price(price, stock.offer)
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

    if stock.offer.isFromAllocine:
        # fmt: off
        updated_fields = {
            attr
            for attr, new_value in updates.items()
            if new_value != getattr(stock, attr)
        }
        # fmt: on
        validation.check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields)
        stock.fieldsUpdated = list(updated_fields)

    for model_attr, value in updates.items():
        setattr(stock, model_attr, value)

    return stock


def _notify_pro_upon_stock_edit_for_event_offer(stock: Stock, bookings: List[Booking]):
    if stock.offer.isEvent:
        if not send_event_offer_postponement_confirmation_email_to_pro(stock, len(bookings)):
            logger.warning(
                "Could not notify pro about update of stock concerning an event offer",
                extra={"stock": stock.id},
            )


def _notify_beneficiaries_upon_stock_edit(stock: Stock, bookings: List[Booking]):
    if bookings:
        bookings = update_cancellation_limit_dates(bookings, stock.beginningDatetime)
        date_in_two_days = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        check_event_is_in_more_than_48_hours = stock.beginningDatetime > date_in_two_days
        if check_event_is_in_more_than_48_hours:
            bookings = _invalidate_bookings(bookings)
        if not send_batch_booking_postponement_email_to_users(bookings):
            logger.warning(
                "Could not notify beneficiaries about update of stock",
                extra={"stock": stock.id},
            )


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
        _update_offer_fraud_information(offer, user)

    for stock in edited_stocks:
        previous_beginning = edited_stocks_previous_beginnings[stock.id]
        if stock.beginningDatetime != previous_beginning and not stock.offer.isEducational:
            bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
            _notify_pro_upon_stock_edit_for_event_offer(stock, bookings)
            _notify_beneficiaries_upon_stock_edit(stock, bookings)
    search.async_index_offer_ids([offer.id])

    return stocks


def _update_offer_fraud_information(offer: Offer, user: User) -> None:
    offer.validation = set_offer_status_based_on_fraud_criteria(offer)
    offer.author = user
    offer.lastValidationDate = datetime.datetime.utcnow()
    if offer.validation == OfferValidationStatus.PENDING or offer.validation == OfferValidationStatus.REJECTED:
        offer.isActive = False
    repository.save(offer)
    if offer.validation == OfferValidationStatus.APPROVED:
        admin_emails.send_offer_creation_notification_to_administration(offer)


def create_educational_stock(stock_data: EducationalStockCreationBodyModel, user: User) -> Stock:
    offer_id = stock_data.offer_id
    beginning = stock_data.beginning_datetime
    booking_limit_datetime = stock_data.booking_limit_datetime
    total_price = stock_data.total_price
    number_of_tickets = stock_data.number_of_tickets
    educational_price_detail = stock_data.educational_price_detail

    offer = Offer.query.filter_by(id=offer_id).options(joinedload(Offer.stocks)).one()
    if len(offer.activeStocks) > 0:
        raise educational_exceptions.EducationalStockAlreadyExists()

    if not offer.isEducational:
        raise educational_exceptions.OfferIsNotEducational(offer_id)
    validation.check_validation_status(offer)
    if booking_limit_datetime is None:
        booking_limit_datetime = beginning

    stock = Stock(
        offer=offer,
        beginningDatetime=beginning,
        bookingLimitDatetime=booking_limit_datetime,
        price=total_price,
        numberOfTickets=number_of_tickets,
        educationalPriceDetail=educational_price_detail,
        quantity=1,
    )
    repository.save(stock)
    logger.info("Educational stock has been created", extra={"offer": offer_id})

    if offer.validation == OfferValidationStatus.DRAFT:
        _update_offer_fraud_information(offer, user)

    search.async_index_offer_ids([offer.id])

    return stock


def edit_educational_stock(stock: Stock, stock_data: dict) -> Stock:
    beginning = stock_data.get("beginningDatetime")
    booking_limit_datetime = stock_data.get("bookingLimitDatetime")

    if not stock.offer.isEducational:
        raise educational_exceptions.OfferIsNotEducational(stock.offerId)

    beginning = as_utc_without_timezone(beginning) if beginning else None
    booking_limit_datetime = as_utc_without_timezone(booking_limit_datetime) if booking_limit_datetime else None

    updatable_fields = _extract_updatable_fields_from_stock_data(stock, stock_data, beginning, booking_limit_datetime)

    validation.check_booking_limit_datetime(stock, beginning, booking_limit_datetime)

    educational_stock_unique_booking = bookings_repository.find_unique_eac_booking_if_any(stock.id)
    if educational_stock_unique_booking:
        validation.check_stock_booking_status(educational_stock_unique_booking)

        educational_stock_unique_booking.educationalBooking.confirmationLimitDate = updatable_fields[
            "bookingLimitDatetime"
        ]
        db.session.add(educational_stock_unique_booking.educationalBooking)

        if beginning:
            _update_educational_booking_cancellation_limit_date(educational_stock_unique_booking, beginning)
            db.session.add(educational_stock_unique_booking)

        if stock_data.get("price"):
            educational_stock_unique_booking.amount = stock_data.get("price")
            db.session.add(educational_stock_unique_booking)

    validation.check_educational_stock_is_editable(stock)

    with transaction():
        stock = offers_repository.get_and_lock_stock(stock.id)
        for attribute, new_value in updatable_fields.items():
            if new_value is not None and getattr(stock, attribute) != new_value:
                setattr(stock, attribute, new_value)
        db.session.add(stock)
        db.session.commit()

    logger.info("Stock has been updated", extra={"stock": stock.id})

    search.async_index_offer_ids([stock.offerId])

    educational_api.notify_educational_redactor_on_educational_offer_or_stock_edit(
        stock.offerId,
        list(stock_data.keys()),
    )

    db.session.refresh(stock)
    return stock


def _extract_updatable_fields_from_stock_data(
    stock: Stock, stock_data: dict, beginning: datetime.datetime, booking_limit_datetime: datetime.datetime
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
        "educationalPriceDetail": stock_data.get("educationalPriceDetail"),
    }

    return updatable_fields


def _update_educational_booking_cancellation_limit_date(
    booking: Booking, new_beginning_datetime: datetime.datetime
) -> None:
    booking.cancellationLimitDate = compute_educational_booking_cancellation_limit_date(
        new_beginning_datetime, datetime.datetime.utcnow()
    )


def _invalidate_bookings(bookings: list[Booking]) -> list[Booking]:
    for booking in bookings:
        if booking.status is BookingStatus.USED:
            mark_as_unused(booking)
    return bookings


def delete_stock(stock: Stock) -> None:
    validation.check_stock_is_deletable(stock)

    stock.isSoftDeleted = True
    repository.save(stock)

    # the algolia sync for the stock will happen within this function
    cancelled_bookings = cancel_bookings_from_stock_by_offerer(stock)

    logger.info(
        "Deleted stock and cancelled its bookings",
        extra={"stock": stock.id, "bookings": [b.id for b in cancelled_bookings]},
    )
    if cancelled_bookings:
        for booking in cancelled_bookings:
            if not send_booking_cancellation_by_pro_to_beneficiary_email(booking):
                logger.warning(
                    "Could not notify beneficiary about deletion of stock",
                    extra={"stock": stock.id, "booking": booking.id},
                )
        if not send_booking_cancellation_confirmation_by_pro_email(cancelled_bookings):
            logger.warning(
                "Could not notify offerer about deletion of stock",
                extra={"stock": stock.id},
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


def update_stock_id_at_providers(venue: Venue, old_siret: str) -> None:
    current_siret = venue.siret

    stocks = (
        Stock.query.join(Offer).filter(Offer.venueId == venue.id).filter(Stock.idAtProviders.endswith(old_siret)).all()
    )

    stock_ids_already_migrated = []
    stocks_to_update = []

    for stock in stocks:
        new_id_at_providers = stock.idAtProviders.replace(old_siret, current_siret)
        if db.session.query(Stock.query.filter_by(idAtProviders=new_id_at_providers).exists()).scalar():
            stock_ids_already_migrated.append(stock.id)
            continue
        stock.idAtProviders = new_id_at_providers
        stocks_to_update.append(stock)

    logger.warning(
        "The following stocks are already migrated from old siret to new siret: [%s]",
        stock_ids_already_migrated,
        extra={"venueId": venue.id, "current_siret": venue.siret, "old_siret": old_siret},
    )

    repository.save(*stocks_to_update)


def get_expense_domains(offer: Offer) -> list[ExpenseDomain]:
    domains = {ExpenseDomain.ALL.value}

    for deposit_type in deposit_conf.SPECIFIC_CAPS:
        for version in deposit_conf.SPECIFIC_CAPS[deposit_type]:
            specific_caps = deposit_conf.SPECIFIC_CAPS[deposit_type][version]
            if specific_caps.digital_cap_applies(offer):
                domains.add(ExpenseDomain.DIGITAL.value)
            if specific_caps.physical_cap_applies(offer):
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


def unindex_expired_offers(process_all_expired: bool = False) -> None:
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


def is_activation_code_applicable(stock: Stock) -> bool:
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


def cancel_educational_offer_booking(offer: Offer) -> None:
    if offer.activeStocks is None or len(offer.activeStocks) == 0:
        raise offers_exceptions.StockNotFound()

    if len(offer.activeStocks) > 1:
        raise offers_exceptions.EducationalOfferHasMultipleStocks()

    stock = offer.activeStocks[0]

    # Offer is reindexed in the end of this function
    cancelled_bookings = cancel_bookings_from_stock_by_offerer(stock)

    if len(cancelled_bookings) == 0:
        raise offers_exceptions.NoBookingToCancel()

    logger.info(
        "Deleted stock and cancelled its bookings",
        extra={"stock": stock.id, "bookings": [b.id for b in cancelled_bookings]},
    )
    for booking in cancelled_bookings:
        try:
            adage_client.notify_booking_cancellation_by_offerer(
                data=serialize_educational_booking(booking.educationalBooking)
            )
        except AdageException as adage_error:
            logger.error(
                "%s Could not notify adage of educational booking cancellation by offerer. Educational institution won't be notified.",
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
    if not send_booking_cancellation_confirmation_by_pro_email(cancelled_bookings):
        logger.warning(
            "Could not notify offerer about deletion of stock",
            extra={"stock": stock.id},
        )


def create_collective_shadow_offer(stock_data: EducationalOfferShadowStockBodyModel, user: User, offer_id: str):
    offer = Offer.query.filter_by(id=offer_id).options(joinedload(Offer.stocks)).one()
    stock = create_educational_shadow_stock_and_set_offer_showcase(stock_data, user, offer)
    create_collective_offer_template_and_delete_regular_collective_offer(offer, stock)
    return stock


def create_collective_offer_template_and_delete_regular_collective_offer(offer: Offer, stock: Stock) -> None:
    collective_offer = educational_models.CollectiveOffer.query.filter_by(offerId=offer.id).one_or_none()
    if collective_offer is None:
        logger.info(
            "Collective offer not found. Collective offer template will be created from old offer model",
            extra={"offer": offer.id},
        )
        collective_offer_template = educational_models.CollectiveOfferTemplate.create_from_offer(
            offer, price_detail=stock.educationalPriceDetail
        )
    else:
        collective_offer_template = educational_models.CollectiveOfferTemplate.create_from_collective_offer(
            collective_offer, price_detail=stock.educationalPriceDetail
        )
        db.session.delete(collective_offer)

    db.session.add(collective_offer_template)
    db.session.commit()
    logger.info(
        "Collective offer template has been created and regular collective offer deleted if applicable",
        extra={"collectiveOfferTemplate": collective_offer_template.id, "offer": offer.id},
    )


def create_educational_shadow_stock_and_set_offer_showcase(
    stock_data: EducationalOfferShadowStockBodyModel, user: User, offer: Offer
) -> Stock:
    # When creating a showcase offer we need to create a shadow stock.
    # We prefill the stock information with false data.
    # This code will disappear when the new collective offer model is implemented
    beginning = datetime.datetime(2030, 1, 1)
    booking_limit_datetime = datetime.datetime(2030, 1, 1)
    total_price = 1
    number_of_tickets = 1
    educational_price_detail = stock_data.educational_price_detail

    if len(offer.activeStocks) > 0:
        raise educational_exceptions.EducationalStockAlreadyExists()

    if not offer.isEducational:
        raise educational_exceptions.OfferIsNotEducational(offer.id)
    validation.check_validation_status(offer)

    stock = Stock(
        offer=offer,
        beginningDatetime=beginning,
        bookingLimitDatetime=booking_limit_datetime,
        price=total_price,
        numberOfTickets=number_of_tickets,
        educationalPriceDetail=educational_price_detail,
        quantity=1,
    )
    repository.save(stock)
    logger.info("Educational shadow stock has been created", extra={"offer": offer.id})

    extra_data = copy.deepcopy(offer.extraData)
    extra_data["isShowcase"] = True
    offer.extraData = extra_data
    repository.save(offer)

    if offer.validation == OfferValidationStatus.DRAFT:
        _update_offer_fraud_information(offer, user)

    search.async_index_offer_ids([offer.id])

    return stock


def transform_shadow_stock_and_create_collective_offer(
    stock_id: str, stock_data: EducationalStockCreationBodyModel, user: User
) -> Stock:
    offer = offers_repository.get_educational_offer_by_id((stock_data.offer_id))
    stock = transform_shadow_stock_into_educational_stock(stock_id, stock_data, offer, user)
    create_collective_offer_and_delete_collective_offer_template(offer)
    return stock


def create_collective_offer_and_delete_collective_offer_template(offer: Offer) -> None:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(
        offerId=offer.id
    ).one_or_none()
    if collective_offer_template is None:
        logger.info(
            "Collective offer template not found. Collective offer will be created from old offer model",
            extra={"offer": offer.id},
        )
        collective_offer = educational_models.CollectiveOffer.create_from_offer(
            offer,
        )
    else:
        collective_offer = educational_models.CollectiveOffer.create_from_collective_offer_template(
            collective_offer_template
        )
        db.session.delete(collective_offer_template)
    db.session.add(collective_offer)
    db.session.commit()


def transform_shadow_stock_into_educational_stock(
    stock_id: str, stock_data: EducationalStockCreationBodyModel, offer: Offer, user: User
) -> Stock:
    if offer.extraData.get("isShowcase") is not True:
        raise educational_exceptions.OfferIsNotShowcase()

    shadow_stock = offers_repository.get_non_deleted_stock_by_id(stock_id)
    validation.check_stock_is_deletable(shadow_stock)
    shadow_stock.isSoftDeleted = True
    db.session.add(shadow_stock)

    stock = create_educational_stock(stock_data, user)
    # commit the changes on shadow_stock once the new stock is created
    db.session.commit()

    extra_data = copy.deepcopy(offer.extraData)
    extra_data["isShowcase"] = False
    offer.extraData = extra_data
    repository.save(offer)

    return stock


def edit_shadow_stock(stock: Stock, stock_data: dict) -> Stock:
    if not stock.offer.isEducational:
        raise educational_exceptions.OfferIsNotEducational(stock.offerId)

    if stock.offer.extraData.get("isShowcase") is not True:
        raise educational_exceptions.OfferIsNotShowcase()

    check_shadow_stock_is_editable(stock)

    with transaction():
        stock = offers_repository.get_and_lock_stock(stock.id)
        if stock_data.get("educational_price_detail") is not None:
            stock.educationalPriceDetail = stock_data["educational_price_detail"]
        db.session.add(stock)
        db.session.commit()

    logger.info("Stock has been updated", extra={"stock": stock.id})

    search.async_index_offer_ids([stock.offerId])

    return stock
