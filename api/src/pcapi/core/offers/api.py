import datetime
import logging
from typing import List
from typing import Optional

from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
from pydantic import ValidationError
import sqlalchemy.exc as sqla_exc
import sqlalchemy.orm as sqla_orm
import yaml
from yaml.scanner import ScannerError

from pcapi import settings
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import remove_thumb
from pcapi.core import search
from pcapi.core.booking_providers.api import get_shows_stock
from pcapi.core.booking_providers.models import VenueBookingProvider
from pcapi.core.bookings.api import cancel_bookings_from_stock_by_offerer
from pcapi.core.bookings.api import cancel_collective_booking_from_stock_by_offerer
from pcapi.core.bookings.api import mark_as_unused
from pcapi.core.bookings.api import update_cancellation_limit_dates
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.categories import subcategories
from pcapi.core.categories.conf import can_create_from_isbn
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.adage_backends as adage_client
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.utils import compute_educational_booking_cancellation_limit_date
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_pro_to_beneficiary import (
    send_booking_cancellation_by_pro_to_beneficiary_email,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_confirmation_by_pro import (
    send_booking_cancellation_confirmation_by_pro_email,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_confirmation_by_pro import (
    send_collective_booking_cancellation_confirmation_by_pro_email,
)
from pcapi.core.mails.transactional.bookings.booking_postponed_by_pro_to_beneficiary import (
    send_batch_booking_postponement_email_to_users,
)
from pcapi.core.mails.transactional.pro.event_offer_postponed_confirmation_to_pro import (
    send_event_offer_postponement_confirmation_email_to_pro,
)
from pcapi.core.mails.transactional.pro.first_venue_approved_offer_to_pro import (
    send_first_venue_approved_offer_email_to_pro,
)
from pcapi.core.mails.transactional.users.reported_offer_by_user import send_email_reported_offer_by_user
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
from pcapi.core.offers.validation import check_booking_limit_datetime
from pcapi.core.offers.validation import check_offer_is_eligible_for_educational
from pcapi.core.offers.validation import check_offer_subcategory_is_valid
from pcapi.core.offers.validation import check_offer_withdrawal
from pcapi.core.offers.validation import check_validation_config_parameters
from pcapi.core.payments import conf as deposit_conf
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import User
from pcapi.domain import admin_emails
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.models.product import Product
from pcapi.repository import offer_queries
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking
from pcapi.routes.serialization.offers_serialize import CompletedEducationalOfferModel
from pcapi.routes.serialization.offers_serialize import PostOfferBodyModel
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.utils import image_conversion
from pcapi.utils.cds import get_cds_show_id_from_uuid
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_raise_error
from pcapi.workers.push_notification_job import send_cancel_booking_notification

from .exceptions import ThumbnailStorageError
from .models import ActivationCode
from .models import Mediation
from .models import WithdrawalTypeEnum


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


def create_offer(
    offer_data: PostOfferBodyModel | CompletedEducationalOfferModel,
    user: User,
    save_as_active: bool = True,
) -> Offer:
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(offer_data.subcategory_id)  # type: ignore [arg-type]
    venue = load_or_raise_error(Venue, offer_data.venue_id)
    check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)  # type: ignore [attr-defined]
    _check_offer_data_is_valid(offer_data, offer_data.is_educational)  # type: ignore [arg-type]
    if _is_able_to_create_book_offer_from_isbn(subcategory):  # type: ignore [arg-type]
        offer = _initialize_book_offer_from_template(offer_data)
    else:
        offer = _initialize_offer_with_new_data(offer_data, subcategory, venue)  # type: ignore [arg-type]

    _complete_common_offer_fields(offer, offer_data, venue)
    offer.isActive = save_as_active

    repository.save(offer)

    logger.info(  # type: ignore [call-arg]
        "Offer has been created",
        extra={"offer_id": offer.id, "venue_id": venue.id, "product_id": offer.productId},  # type: ignore [attr-defined]
        technical_message_id="offer.created",
    )

    update_external_pro(venue.bookingEmail)  # type: ignore [attr-defined]

    return offer


def _is_able_to_create_book_offer_from_isbn(subcategory: subcategories.Subcategory) -> bool:
    return FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION.is_active() and can_create_from_isbn(
        subcategory_id=subcategory.id
    )


def _initialize_book_offer_from_template(offer_data: PostOfferBodyModel | CompletedEducationalOfferModel) -> Offer:
    product = _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(offer_data.extra_data["isbn"])  # type: ignore [index]
    extra_data = product.extraData
    extra_data.update(offer_data.extra_data)  # type: ignore [union-attr]
    offer = Offer(
        product=product,
        subcategoryId=product.subcategoryId,
        name=offer_data.name,
        description=offer_data.description if offer_data.description else product.description,
        url=offer_data.url if offer_data.url else product.url,  # type: ignore [union-attr]
        mediaUrls=offer_data.url if offer_data.url else product.url,  # type: ignore [union-attr]
        conditions=offer_data.conditions if offer_data.conditions else product.conditions,  # type: ignore [union-attr]
        ageMin=offer_data.age_min if offer_data.age_min else product.ageMin,  # type: ignore [union-attr]
        ageMax=offer_data.age_max if offer_data.age_max else product.ageMax,  # type: ignore [union-attr]
        isNational=offer_data.is_national if offer_data.is_national else product.isNational,  # type: ignore [union-attr]
        extraData=extra_data,
    )
    return offer


def _initialize_offer_with_new_data(
    offer_data: PostOfferBodyModel | CompletedEducationalOfferModel,
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
    offer.subcategoryId = subcategory.id if subcategory else None  # type: ignore [assignment]
    offer.product.owningOfferer = venue.managingOfferer
    return offer


def _complete_common_offer_fields(
    offer: Offer,
    offer_data: PostOfferBodyModel | CompletedEducationalOfferModel,
    venue: Venue,
) -> None:
    offer.venue = venue
    offer.bookingEmail = offer_data.booking_email
    offer.externalTicketOfficeUrl = offer_data.external_ticket_office_url
    offer.audioDisabilityCompliant = offer_data.audio_disability_compliant
    offer.mentalDisabilityCompliant = offer_data.mental_disability_compliant
    offer.motorDisabilityCompliant = offer_data.motor_disability_compliant
    offer.visualDisabilityCompliant = offer_data.visual_disability_compliant
    offer.validation = OfferValidationStatus.DRAFT  # type: ignore [assignment]
    offer.isEducational = offer_data.is_educational  # type: ignore [assignment]


def _check_offer_data_is_valid(
    offer_data: PostOfferBodyModel | CompletedEducationalOfferModel,
    offer_is_educational: bool,
) -> None:
    check_offer_subcategory_is_valid(offer_data.subcategory_id)
    check_offer_is_eligible_for_educational(offer_data.subcategory_id, offer_is_educational)  # type: ignore [arg-type]
    if not offer_is_educational:
        validation.check_offer_extra_data(None, offer_data.subcategory_id, offer_data.extra_data)  # type: ignore [arg-type]


def update_offer(
    offer: Offer,
    bookingEmail: str = UNCHANGED,  # type: ignore [assignment]
    description: str = UNCHANGED,  # type: ignore [assignment]
    isNational: bool = UNCHANGED,  # type: ignore [assignment]
    name: str = UNCHANGED,  # type: ignore [assignment]
    extraData: dict = UNCHANGED,  # type: ignore [assignment]
    externalTicketOfficeUrl: str = UNCHANGED,  # type: ignore [assignment]
    url: str = UNCHANGED,  # type: ignore [assignment]
    withdrawalDetails: str = UNCHANGED,  # type: ignore [assignment]
    withdrawalType: WithdrawalTypeEnum = UNCHANGED,  # type: ignore [assignment]
    withdrawalDelay: int = UNCHANGED,  # type: ignore [assignment]
    isActive: bool = UNCHANGED,  # type: ignore [assignment]
    isDuo: bool = UNCHANGED,  # type: ignore [assignment]
    durationMinutes: int = UNCHANGED,  # type: ignore [assignment]
    mediaUrls: list[str] = UNCHANGED,  # type: ignore [assignment]
    ageMin: int = UNCHANGED,  # type: ignore [assignment]
    ageMax: int = UNCHANGED,  # type: ignore [assignment]
    conditions: str = UNCHANGED,  # type: ignore [assignment]
    venueId: str = UNCHANGED,  # type: ignore [assignment]
    productId: str = UNCHANGED,  # type: ignore [assignment]
    audioDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
    mentalDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
    motorDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
    visualDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
) -> Offer:
    validation.check_validation_status(offer)
    if extraData != UNCHANGED:
        extraData = validation.check_offer_extra_data(offer, offer.subcategoryId, extraData)

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

    if (UNCHANGED, UNCHANGED) != (withdrawalType, withdrawalDelay):
        try:
            changed_withdrawalType = withdrawalType if withdrawalType != UNCHANGED else offer.withdrawalType
            changed_withdrawalDelay = withdrawalDelay if withdrawalDelay != UNCHANGED else offer.withdrawalDelay
            check_offer_withdrawal(changed_withdrawalType, changed_withdrawalDelay, offer.subcategoryId)  # type: ignore [arg-type]
        except offers_exceptions.OfferCreationBaseException as error:
            raise ApiErrors(
                error.errors,
                status_code=400,
            )

    if offer.isFromProvider:
        validation.check_update_only_allowed_fields_for_offer_from_provider(set(modifications), offer.lastProvider)

    offer.populate_from_dict(modifications)
    with db.session.no_autoflush:
        if offer.product.owningOfferer and offer.product.owningOfferer == offer.venue.managingOfferer:
            offer.product.populate_from_dict(modifications)
            product_has_been_updated = True
        else:
            product_has_been_updated = False

    if offer.isFromAllocine:
        offer.fieldsUpdated = list(set(offer.fieldsUpdated) | set(modifications))

    repository.save(offer)

    logger.info("Offer has been updated", extra={"offer_id": offer.id}, technical_message_id="offer.updated")  # type: ignore [call-arg]
    if product_has_been_updated:
        repository.save(offer.product)
        logger.info("Product has been updated", extra={"product": offer.product.id})

    search.async_index_offer_ids([offer.id])

    return offer


def update_collective_offer(
    offer_id: int,
    is_offer_showcase: bool,
    new_values: dict,
) -> None:
    cls = educational_models.CollectiveOfferTemplate if is_offer_showcase else educational_models.CollectiveOffer

    offer_to_update = cls.query.filter(cls.id == offer_id).first()  # type: ignore [attr-defined]

    if offer_to_update is None:
        # FIXME (MathildeDuboille - 2022-03-07): raise an error once all data has been migrated (PC-13427)
        return

    updated_fields = _update_collective_offer(offer=offer_to_update, new_values=new_values)

    if is_offer_showcase:
        search.async_index_collective_offer_template_ids([offer_to_update.id])
    else:
        search.async_index_collective_offer_ids([offer_to_update.id])

    if not is_offer_showcase:
        educational_api.notify_educational_redactor_on_collective_offer_or_stock_edit(
            offer_to_update.id,
            updated_fields,
        )


def update_collective_offe_template(offer_id: int, new_values: dict) -> None:
    query = educational_models.CollectiveOfferTemplate.query
    query = query.filter(educational_models.CollectiveOfferTemplate.id == offer_id)
    offer_to_update = query.first()
    _update_collective_offer(offer=offer_to_update, new_values=new_values)
    search.async_index_collective_offer_template_ids([offer_to_update.id])


def _update_collective_offer(offer: CollectiveOffer | CollectiveOfferTemplate, new_values: dict) -> list[str]:
    validation.check_validation_status(offer)
    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():
        updated_fields.append(key)

        if key == "subcategoryId":
            validation.check_offer_is_eligible_for_educational(value.name, True)
            offer.subcategoryId = value.name
            continue

        if key == "domains":
            domains = educational_api.get_educational_domains_from_ids(value)
            offer.domains = domains
            continue

        setattr(offer, key, value)
    db.session.add(offer)
    db.session.commit()
    return updated_fields


def batch_update_offers(query, update_fields):  # type: ignore [no-untyped-def]
    raw_results = (
        query.filter(Offer.validation == OfferValidationStatus.APPROVED).with_entities(Offer.id, Offer.venueId).all()
    )
    offer_ids, venue_ids = [], []
    if raw_results:
        offer_ids, venue_ids = zip(*raw_results)
    venue_ids = sorted(set(venue_ids))
    logger.info(
        "Batch update of offers",
        extra={"updated_fields": update_fields, "nb_offers": len(offer_ids), "venue_ids": venue_ids},
    )

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


def batch_update_collective_offers(query, update_fields):  # type: ignore [no-untyped-def]
    collective_offer_ids_tuples = query.filter(
        CollectiveOffer.validation == OfferValidationStatus.APPROVED
    ).with_entities(CollectiveOffer.id)

    collective_offer_ids = [offer_id for offer_id, in collective_offer_ids_tuples]
    number_of_collective_offers_to_update = len(collective_offer_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_to_update, batch_size):
        collective_offer_ids_batch = collective_offer_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_to_update)
        ]

        query_to_update = CollectiveOffer.query.filter(CollectiveOffer.id.in_(collective_offer_ids_batch))
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.commit()

        search.async_index_collective_offer_ids(collective_offer_ids_batch)


def batch_update_collective_offers_template(query, update_fields):  # type: ignore [no-untyped-def]
    collective_offer_ids_tuples = query.filter(
        CollectiveOfferTemplate.validation == OfferValidationStatus.APPROVED
    ).with_entities(CollectiveOfferTemplate.id)

    collective_offer_template_ids = [offer_id for offer_id, in collective_offer_ids_tuples]
    number_of_collective_offers_template_to_update = len(collective_offer_template_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_template_to_update, batch_size):
        collective_offer_template_ids_batch = collective_offer_template_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_template_to_update)
        ]

        query_to_update = CollectiveOfferTemplate.query.filter(
            CollectiveOfferTemplate.id.in_(collective_offer_template_ids_batch)
        )
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.commit()

        search.async_index_collective_offer_template_ids(collective_offer_template_ids_batch)


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
        stock.fieldsUpdated = list(set(stock.fieldsUpdated) | updated_fields)

    for model_attr, value in updates.items():
        setattr(stock, model_attr, value)

    return stock


def _notify_pro_upon_stock_edit_for_event_offer(stock: Stock, bookings: List[Booking]):  # type: ignore [no-untyped-def]
    if stock.offer.isEvent:
        if not send_event_offer_postponement_confirmation_email_to_pro(stock, len(bookings)):
            logger.warning(
                "Could not notify pro about update of stock concerning an event offer",
                extra={"stock": stock.id},
            )


def _notify_beneficiaries_upon_stock_edit(stock: Stock, bookings: List[Booking]):  # type: ignore [no-untyped-def]
    if bookings:
        bookings = update_cancellation_limit_dates(bookings, stock.beginningDatetime)  # type: ignore [arg-type]
        date_in_two_days = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        check_event_is_in_more_than_48_hours = stock.beginningDatetime > date_in_two_days  # type: ignore [operator]
        if check_event_is_in_more_than_48_hours:
            bookings = _invalidate_bookings(bookings)
        if not send_batch_booking_postponement_email_to_users(bookings):
            logger.warning(
                "Could not notify beneficiaries about update of stock",
                extra={"stock": stock.id},
            )


def upsert_stocks(
    offer_id: int, stock_data_list: list[StockCreationBodyModel | StockEditionBodyModel], user: User
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
                .options(sqla_orm.joinedload(Stock.activationCodes))
                .first_or_404()
            )
            if stock.offerId != offer_id:
                errors = ApiErrors()
                errors.add_error(
                    "global", "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
                )
                errors.status_code = 403
                raise errors
            check_booking_limit_datetime(stock, stock_data.beginning_datetime, stock_data.booking_limit_datetime)
            edited_stocks_previous_beginnings[stock.id] = stock.beginningDatetime

            booking_limit_datetime = stock_data.booking_limit_datetime or stock.bookingLimitDatetime
            beginning = stock_data.beginning_datetime or stock.beginningDatetime
            if beginning and booking_limit_datetime and beginning > booking_limit_datetime:
                booking_limit_datetime = beginning

            edited_stock = _edit_stock(
                stock,
                price=stock_data.price,
                quantity=stock_data.quantity,  # type: ignore [arg-type]
                beginning=stock_data.beginning_datetime,  # type: ignore [arg-type]
                booking_limit_datetime=booking_limit_datetime,
            )
            edited_stocks.append(edited_stock)
            stocks.append(edited_stock)
        else:
            check_booking_limit_datetime(None, stock_data.beginning_datetime, stock_data.booking_limit_datetime)

            activation_codes_exist = stock_data.activation_codes is not None and len(stock_data.activation_codes) > 0

            if activation_codes_exist:
                validation.check_offer_is_digital(offer)
                validation.check_activation_codes_expiration_datetime(
                    stock_data.activation_codes_expiration_datetime,
                    stock_data.booking_limit_datetime,
                )

            quantity = len(stock_data.activation_codes) if activation_codes_exist else stock_data.quantity  # type: ignore[arg-type]

            booking_limit_datetime = stock_data.booking_limit_datetime
            if (
                stock_data.beginning_datetime
                and booking_limit_datetime
                and stock_data.beginning_datetime > booking_limit_datetime
            ):
                booking_limit_datetime = stock_data.beginning_datetime

            created_stock = _create_stock(
                offer=offer,
                price=stock_data.price,
                quantity=quantity,
                beginning=stock_data.beginning_datetime,
                booking_limit_datetime=booking_limit_datetime,
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
    if not FeatureToggle.OFFER_FORM_SUMMARY_PAGE.is_active():
        if offer.validation == OfferValidationStatus.DRAFT:
            update_offer_fraud_information(offer, user)

    for stock in edited_stocks:
        previous_beginning = edited_stocks_previous_beginnings[stock.id]
        if stock.beginningDatetime != previous_beginning and not stock.offer.isEducational:
            bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
            _notify_pro_upon_stock_edit_for_event_offer(stock, bookings)
            _notify_beneficiaries_upon_stock_edit(stock, bookings)

    if not FeatureToggle.OFFER_FORM_SUMMARY_PAGE.is_active() or edited_stocks:
        search.async_index_offer_ids([offer.id])

    return stocks


def publish_offer(offer_id: int, user: User) -> Offer:
    offer = offers_repository.get_offer_by_id(offer_id)
    offer.isActive = True
    update_offer_fraud_information(offer, user)
    search.async_index_offer_ids([offer.id])
    return offer


def update_offer_fraud_information(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate | Offer,
    user: User,
    *,
    silent: bool = False,
) -> None:
    venue_already_has_validated_offer = offers_repository.venue_already_has_validated_offer(offer)

    offer.validation = set_offer_status_based_on_fraud_criteria(offer)  # type: ignore [assignment]
    offer.author = user
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO  # type: ignore [assignment]

    if offer.validation in (OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED):
        offer.isActive = False
    repository.save(offer)
    if offer.validation == OfferValidationStatus.APPROVED and not silent:
        admin_emails.send_offer_creation_notification_to_administration(offer)

    if (
        offer.validation == OfferValidationStatus.APPROVED
        and not offer.isEducational
        and not venue_already_has_validated_offer
    ):
        if not send_first_venue_approved_offer_email_to_pro(offer):
            logger.warning("Could not send first venue approved offer email", extra={"offer_id": offer.id})


def _update_educational_booking_cancellation_limit_date(
    booking: Booking | educational_models.CollectiveBooking, new_beginning_datetime: datetime.datetime
) -> None:
    booking.cancellationLimitDate = compute_educational_booking_cancellation_limit_date(  # type: ignore [assignment]
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
    crop_params: Optional[image_conversion.CropParams] = None,
    keep_ratio: bool = False,
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
        create_thumb(mediation, image_as_bytes, image_index=0, crop_params=crop_params, keep_ratio=keep_ratio)
    except image_conversion.ImageRatioError:
        raise
    except Exception as exception:
        logger.exception("An unexpected error was encountered during the thumbnail creation: %s", exception)
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
            except Exception as exception:  # pylint: disable=broad-except
                logger.exception(
                    "An unexpected error was encountered during the thumbnails deletion for %s: %s",
                    mediation,
                    exception,
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

    for _deposit_type, versions in deposit_conf.SPECIFIC_CAPS.items():
        for _version, specific_caps in versions.items():  # type: ignore [attr-defined]
            if specific_caps.digital_cap_applies(offer):
                domains.add(ExpenseDomain.DIGITAL.value)
            if specific_caps.physical_cap_applies(offer):
                domains.add(ExpenseDomain.PHYSICAL.value)

    return list(domains)  # type: ignore [arg-type]


def add_criteria_to_offers(
    criteria: list[criteria_models.Criterion],
    isbn: Optional[str] = None,
    visa: Optional[str] = None,
) -> bool:
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

    # check existing tags on selected offers to avoid duplicate association which would violate Unique constraint
    existing_criteria_on_offers = (
        criteria_models.OfferCriterion.query.filter(criteria_models.OfferCriterion.offerId.in_(offer_ids))
        .with_entities(criteria_models.OfferCriterion.offerId, criteria_models.OfferCriterion.criterionId)
        .all()
    )

    offer_criteria: list[criteria_models.OfferCriterion] = []
    for criterion in criteria:
        logger.info("Adding criterion %s to %d offers", criterion, len(offer_ids))
        for offer_id in offer_ids:
            if not (offer_id, criterion.id) in existing_criteria_on_offers:
                offer_criteria.append(
                    criteria_models.OfferCriterion(
                        offerId=offer_id,
                        criterionId=criterion.id,
                    )
                )

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


def deactivate_permanently_unavailable_products(isbn: str) -> bool:
    products = Product.query.filter(Product.extraData["isbn"].astext == isbn).all()
    if not products:
        return False

    for product in products:
        product.name = "xxx"
        db.session.add(product)

    offers = Offer.query.filter(Offer.productId.in_(p.id for p in products)).filter(Offer.isActive.is_(True))
    offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id).all()]
    offers.update(values={"isActive": False, "name": "xxx"}, synchronize_session="fetch")

    try:
        db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark product and offers as permanently unavailable: %s",
            extra={"isbn": isbn, "products": [p.id for p in products], "exc": str(exception)},
        )
        return False
    logger.info(
        "Deactivated permanently unavailable products",
        extra={"isbn": isbn, "products": [p.id for p in products], "offers": offer_ids},
    )

    search.async_index_offer_ids(offer_ids)

    return True


def set_offer_status_based_on_fraud_criteria(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate | Offer,
) -> OfferValidationStatus:
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

    offer = type(offer).query.filter_by(id=offer.id).one()
    if offer.validation != OfferValidationStatus.PENDING:
        template = f"{type(offer)} validation status cannot be updated, initial validation status is not PENDING. %s"
        logger.info(template, extra={"offer": offer.id})
        return False
    offer.validation = validation_status  # type: ignore [assignment]
    if validation_status == OfferValidationStatus.APPROVED:
        offer.isActive = True

    try:
        db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        template = f"Could not update {type(offer)} validation status: %s"
        logger.exception(
            template,
            extra={"offer": offer.id, "validation_status": validation_status, "exc": str(exception)},
        )
        return False
    if isinstance(offer, Offer):
        search.async_index_offer_ids([offer.id])
    elif isinstance(offer, CollectiveOffer):
        search.async_index_collective_offer_ids([offer.id])
    elif isinstance(offer, CollectiveOfferTemplate):
        search.async_index_collective_offer_template_ids([offer.id])
    template = f"{type(offer)} validation status updated"
    logger.info(template, extra={"offer": offer.id})
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
        raise WrongFormatInFraudConfigurationFile(str(error))  # type: ignore [arg-type]

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
    except sqla_exc.IntegrityError as error:
        if error.orig.pgcode == UNIQUE_VIOLATION:
            raise OfferAlreadyReportedError() from error
        if error.orig.pgcode == CHECK_VIOLATION:
            raise ReportMalformed() from error
        raise

    if not send_email_reported_offer_by_user(user, offer, reason, custom_reason):
        logger.warning("Could not send email reported offer by user", extra={"user_id": user.id})


def cancel_collective_offer_booking(offer_id: int) -> None:
    collective_offer = CollectiveOffer.query.filter(CollectiveOffer.id == offer_id).first()

    if collective_offer.collectiveStock is None:
        raise offers_exceptions.StockNotFound()

    collective_stock = collective_offer.collectiveStock

    # Offer is reindexed in the end of this function
    cancelled_booking = cancel_collective_booking_from_stock_by_offerer(collective_stock)

    if cancelled_booking is None:
        raise offers_exceptions.NoBookingToCancel()

    search.async_index_collective_offer_ids([offer_id])

    logger.info(
        "Deleted collective stock and cancelled its collective booking",
        extra={"stock": collective_stock.id, "collective_booking": cancelled_booking.id},
    )

    try:
        adage_client.notify_booking_cancellation_by_offerer(data=serialize_collective_booking(cancelled_booking))
    except educational_exceptions.AdageException as adage_error:
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
            "Could not notify adage of prebooking, hence send confirmation email to educational institution, as educationalBooking serialization failed.",
            extra={
                "collectiveBookingId": cancelled_booking.id,
            },
        )
    if not send_collective_booking_cancellation_confirmation_by_pro_email(cancelled_booking):
        logger.warning(
            "Could not notify offerer about deletion of stock",
            extra={"collectiveStock": collective_stock.id},
        )


def update_stock_quantity_to_match_booking_provider_remaining_place(offer: Offer) -> None:
    booking_provider = VenueBookingProvider.query.filter(
        VenueBookingProvider.venueId == offer.venueId, VenueBookingProvider.isActive
    ).one_or_none()

    if not booking_provider:
        return

    shows_id = [
        int(get_cds_show_id_from_uuid(stock.idAtProviders)) for stock in offer.activeStocks if stock.idAtProviders
    ]

    if not shows_id:
        return

    logger.info(
        "Getting up-to-date show stock from booking provider on offer view",
        extra={"offer": offer.id, "booking_provider": booking_provider.id},
    )
    shows_remaining_places = get_shows_stock(offer.venueId, shows_id)

    for show_id, remaining_places in shows_remaining_places.items():
        stock = next((s for s in offer.activeStocks if get_cds_show_id_from_uuid(s.idAtProviders) == str(show_id)))
        if stock:
            if remaining_places <= 0:
                stock.quantity = stock.dnBookedQuantity
                repository.save(stock)
