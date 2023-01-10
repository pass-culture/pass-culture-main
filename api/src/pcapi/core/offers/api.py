import datetime
import decimal
import logging
import typing

from flask_sqlalchemy import BaseQuery
from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
import sentry_sdk
import sqlalchemy.exc as sqla_exc
import sqlalchemy.orm as sqla_orm
import yaml
from yaml.scanner import ScannerError

from pcapi import settings
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
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.external.attributes.api import update_external_pro
import pcapi.core.external_bookings.api as external_bookings_api
import pcapi.core.finance.conf as finance_conf
import pcapi.core.mails.transactional as transactional_mails
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
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.offers.offer_validation import compute_offer_validation_score
from pcapi.core.offers.offer_validation import parse_offer_validation_config
import pcapi.core.offers.repository as offers_repository
from pcapi.core.offers.repository import update_stock_quantity_to_dn_booked_quantity
from pcapi.core.offers.utils import as_utc_without_timezone
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import User
from pcapi.domain import admin_emails
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.models import db
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.utils import image_conversion
import pcapi.utils.cinema_providers as cinema_providers_utils
from pcapi.workers import push_notification_job

from . import exceptions
from . import models
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
    category_id: str | None,
    offerer_id: int | None,
    venue_id: int | None = None,
    name_keywords_or_isbn: str | None = None,
    status: str | None = None,
    creation_mode: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
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
    audio_disability_compliant: bool,
    mental_disability_compliant: bool,
    motor_disability_compliant: bool,
    name: str,
    subcategory_id: str,
    venue: Venue,
    visual_disability_compliant: bool,
    booking_email: str | None = None,
    description: str | None = None,
    duration_minutes: int | None = None,
    external_ticket_office_url: str | None = None,
    extra_data: typing.Any = None,
    is_duo: bool | None = None,
    is_national: bool | None = None,
    provider: providers_models.Provider | None = None,
    url: str | None = None,
    withdrawal_delay: int | None = None,
    withdrawal_details: str | None = None,
    withdrawal_type: models.WithdrawalTypeEnum | None = None,
) -> Offer:
    validation.check_offer_withdrawal(withdrawal_type, withdrawal_delay, subcategory_id)
    validation.check_offer_subcategory_is_valid(subcategory_id)
    validation.check_offer_extra_data(subcategory_id, extra_data)
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id]
    validation.check_is_duo_compliance(is_duo, subcategory)

    if _is_able_to_create_book_offer_from_isbn(subcategory):
        offer = _initialize_book_offer_from_template(description, extra_data, is_national, name, url)
    else:
        offer = _initialize_offer_with_new_data(
            description,
            duration_minutes,
            extra_data,
            is_duo,
            is_national,
            name,
            subcategory_id,
            url,
            venue,
            withdrawal_delay,
            withdrawal_details,
            withdrawal_type,
        )

    offer.audioDisabilityCompliant = audio_disability_compliant
    offer.bookingEmail = booking_email
    offer.externalTicketOfficeUrl = external_ticket_office_url
    offer.isActive = False
    offer.mentalDisabilityCompliant = mental_disability_compliant
    offer.motorDisabilityCompliant = motor_disability_compliant
    offer.lastProvider = provider
    offer.validation = OfferValidationStatus.DRAFT
    offer.venue = venue
    offer.visualDisabilityCompliant = visual_disability_compliant

    repository.add_to_session(offer)

    logger.info(  # type: ignore [call-arg]
        "Offer has been created",
        extra={"offer_id": offer.id, "venue_id": venue.id, "product_id": offer.productId},
        technical_message_id="offer.created",
    )

    update_external_pro(venue.bookingEmail)

    return offer


def _is_able_to_create_book_offer_from_isbn(subcategory: subcategories.Subcategory) -> bool:
    # TODO(viconnex): add check on isbn presence
    return FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION.is_active() and can_create_from_isbn(
        subcategory_id=subcategory.id
    )


def _initialize_book_offer_from_template(
    description: str | None,
    extra_data: typing.Any,
    is_national: bool | None,
    name: str,
    url: str | None,
) -> Offer:
    product = _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(extra_data["isbn"])

    offer = Offer(
        ageMax=product.ageMax,
        ageMin=product.ageMin,
        conditions=product.conditions,
        description=description if description else product.description,
        extraData=product.extraData | extra_data,
        isNational=is_national if is_national else product.isNational,
        name=name,
        product=product,
        subcategoryId=product.subcategoryId,
        url=url if url else product.url,
    )
    return offer


def _initialize_offer_with_new_data(
    description: str | None,
    duration_minutes: int | None,
    extra_data: typing.Any,
    is_duo: bool | None,
    is_national: bool | None,
    name: str,
    subcategory_id: str,
    url: str | None,
    venue: Venue,
    withdrawal_delay: int | None,
    withdrawal_details: str | None,
    withdrawal_type: models.WithdrawalTypeEnum | None,
) -> Offer:
    is_national = True if url else bool(is_national)
    product = Product(
        name=name,
        description=description,
        url=url,
        durationMinutes=duration_minutes,
        isNational=bool(is_national),
        owningOfferer=venue.managingOfferer,
        subcategoryId=subcategory_id,
    )

    offer = Offer(
        description=description,
        durationMinutes=duration_minutes,
        extraData=extra_data,
        isDuo=bool(is_duo),
        isNational=bool(is_national),
        name=name,
        product=product,
        subcategoryId=subcategory_id,
        url=url,
        withdrawalDelay=withdrawal_delay,
        withdrawalDetails=withdrawal_details,
        withdrawalType=withdrawal_type,
    )

    return offer


def update_offer(
    offer: Offer,
    bookingEmail: str | None = UNCHANGED,  # type: ignore [assignment]
    description: str | None = UNCHANGED,  # type: ignore [assignment]
    isNational: bool = UNCHANGED,  # type: ignore [assignment]
    name: str = UNCHANGED,  # type: ignore [assignment]
    extraData: dict | None = UNCHANGED,  # type: ignore [assignment]
    externalTicketOfficeUrl: str | None = UNCHANGED,  # type: ignore [assignment]
    url: str | None = UNCHANGED,  # type: ignore [assignment]
    withdrawalDetails: str | None = UNCHANGED,  # type: ignore [assignment]
    withdrawalType: WithdrawalTypeEnum | None = UNCHANGED,  # type: ignore [assignment]
    withdrawalDelay: int | None = UNCHANGED,  # type: ignore [assignment]
    isActive: bool = UNCHANGED,  # type: ignore [assignment]
    isDuo: bool = UNCHANGED,  # type: ignore [assignment]
    durationMinutes: int | None = UNCHANGED,  # type: ignore [assignment]
    mediaUrls: list[str] | None = UNCHANGED,  # type: ignore [assignment]
    ageMin: int | None = UNCHANGED,  # type: ignore [assignment]
    ageMax: int | None = UNCHANGED,  # type: ignore [assignment]
    conditions: str | None = UNCHANGED,  # type: ignore [assignment]
    venueId: str = UNCHANGED,  # type: ignore [assignment]
    productId: str = UNCHANGED,  # type: ignore [assignment]
    audioDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
    mentalDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
    motorDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
    visualDisabilityCompliant: bool = UNCHANGED,  # type: ignore [assignment]
) -> Offer:
    validation.check_validation_status(offer)
    if extraData != UNCHANGED:
        validation.check_offer_extra_data(offer.subcategoryId, extraData)

    modifications = {
        field: new_value
        for field, new_value in locals().items()
        if field != "offer"
        and new_value is not UNCHANGED  # has the user provided a value for this field
        and getattr(offer, field) != new_value  # is the value different from what we have on database?
    }
    if not modifications:
        return offer

    if (UNCHANGED, UNCHANGED) != (withdrawalType, withdrawalDelay):
        try:
            changed_withdrawalType = withdrawalType if withdrawalType != UNCHANGED else offer.withdrawalType
            changed_withdrawalDelay = withdrawalDelay if withdrawalDelay != UNCHANGED else offer.withdrawalDelay
            validation.check_offer_withdrawal(changed_withdrawalType, changed_withdrawalDelay, offer.subcategoryId)
        except offers_exceptions.OfferCreationBaseException as error:
            raise ApiErrors(error.errors, status_code=400)

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
    new_values: dict,
) -> None:
    offer_to_update = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id == offer_id
    ).first()

    updated_fields = _update_collective_offer(offer=offer_to_update, new_values=new_values)

    search.async_index_collective_offer_ids([offer_to_update.id])

    educational_api_offer.notify_educational_redactor_on_collective_offer_or_stock_edit(
        offer_to_update.id,
        updated_fields,
    )


def update_collective_offer_template(offer_id: int, new_values: dict) -> None:
    query = educational_models.CollectiveOfferTemplate.query
    query = query.filter(educational_models.CollectiveOfferTemplate.id == offer_id)
    offer_to_update = query.first()
    _update_collective_offer(offer=offer_to_update, new_values=new_values)
    search.async_index_collective_offer_template_ids([offer_to_update.id])


def _update_collective_offer(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate, new_values: dict
) -> list[str]:
    validation.check_validation_status(offer)
    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():
        updated_fields.append(key)

        if key == "subcategoryId":
            validation.check_offer_is_eligible_for_educational(value.name)
            offer.subcategoryId = value.name
            continue

        if key == "domains":
            domains = educational_api_offer.get_educational_domains_from_ids(value)
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
    if "isActive" in update_fields.keys():
        if update_fields["isActive"]:
            logger.info(
                "Offers has been activated",
                extra={"offer_ids": offer_ids, "venue_id": venue_ids},
                technical_message_id="offers.activated",
            )
        else:
            logger.info(
                "Offers has been deactivated",
                extra={"offer_ids": offer_ids, "venue_id": venue_ids},
                technical_message_id="offers.deactivated",
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
        educational_models.CollectiveOffer.validation == OfferValidationStatus.APPROVED
    ).with_entities(educational_models.CollectiveOffer.id)

    collective_offer_ids = [offer_id for offer_id, in collective_offer_ids_tuples]
    number_of_collective_offers_to_update = len(collective_offer_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_to_update, batch_size):
        collective_offer_ids_batch = collective_offer_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_to_update)
        ]

        query_to_update = educational_models.CollectiveOffer.query.filter(
            educational_models.CollectiveOffer.id.in_(collective_offer_ids_batch)
        )
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.commit()

        search.async_index_collective_offer_ids(collective_offer_ids_batch)


def batch_update_collective_offers_template(query, update_fields):  # type: ignore [no-untyped-def]
    collective_offer_ids_tuples = query.filter(
        educational_models.CollectiveOfferTemplate.validation == OfferValidationStatus.APPROVED
    ).with_entities(educational_models.CollectiveOfferTemplate.id)

    collective_offer_template_ids = [offer_id for offer_id, in collective_offer_ids_tuples]
    number_of_collective_offers_template_to_update = len(collective_offer_template_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_template_to_update, batch_size):
        collective_offer_template_ids_batch = collective_offer_template_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_template_to_update)
        ]

        query_to_update = educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.id.in_(collective_offer_template_ids_batch)
        )
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.commit()

        search.async_index_collective_offer_template_ids(collective_offer_template_ids_batch)


def _notify_pro_upon_stock_edit_for_event_offer(stock: Stock, bookings: typing.List[Booking]):  # type: ignore [no-untyped-def]
    if stock.offer.isEvent:
        if not transactional_mails.send_event_offer_postponement_confirmation_email_to_pro(stock, len(bookings)):
            logger.warning(
                "Could not notify pro about update of stock concerning an event offer",
                extra={"stock": stock.id},
            )


def _notify_beneficiaries_upon_stock_edit(stock: Stock, bookings: typing.List[Booking]):  # type: ignore [no-untyped-def]
    if bookings:
        bookings = update_cancellation_limit_dates(bookings, stock.beginningDatetime)  # type: ignore [arg-type]
        date_in_two_days = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        check_event_is_in_more_than_48_hours = stock.beginningDatetime > date_in_two_days  # type: ignore [operator]
        if check_event_is_in_more_than_48_hours:
            bookings = _invalidate_bookings(bookings)
        if not transactional_mails.send_batch_booking_postponement_email_to_users(bookings):
            logger.warning(
                "Could not notify beneficiaries about update of stock",
                extra={"stock": stock.id},
            )


def create_stock(
    offer: Offer,
    price: decimal.Decimal,
    quantity: int | None,
    activation_codes: list[str] | None = None,
    activation_codes_expiration_datetime: datetime.datetime | None = None,
    beginning_datetime: datetime.datetime | None = None,
    booking_limit_datetime: datetime.datetime | None = None,
    creating_provider: providers_models.Provider | None = None,
) -> Stock:
    validation.check_booking_limit_datetime(None, beginning_datetime, booking_limit_datetime)

    activation_codes = activation_codes or []
    if activation_codes:
        validation.check_offer_is_digital(offer)
        validation.check_activation_codes_expiration_datetime(
            activation_codes_expiration_datetime,
            booking_limit_datetime,
        )
        quantity = len(activation_codes)

    if beginning_datetime and booking_limit_datetime and beginning_datetime < booking_limit_datetime:
        booking_limit_datetime = beginning_datetime

    validation.check_required_dates_for_stock(offer, beginning_datetime, booking_limit_datetime)
    validation.check_validation_status(offer)
    validation.check_provider_can_create_stock(offer, creating_provider)
    validation.check_stock_price(price, offer)
    validation.check_stock_quantity(quantity)

    created_stock = Stock(
        offerId=offer.id,
        price=decimal.Decimal(price),
        quantity=quantity,
        beginningDatetime=beginning_datetime,
        bookingLimitDatetime=booking_limit_datetime,
    )
    created_activation_codes = []

    for activation_code in activation_codes:
        created_activation_codes.append(
            ActivationCode(
                code=activation_code,
                expirationDate=activation_codes_expiration_datetime,
                stock=created_stock,
            )
        )
    repository.add_to_session(created_stock, *created_activation_codes)

    return created_stock


def edit_stock(
    offer: Offer,
    price: decimal.Decimal,
    quantity: int | None,
    stock_id: int,
    beginning_datetime: datetime.datetime | None = None,
    booking_limit_datetime: datetime.datetime | None = None,
    editing_provider: providers_models.Provider | None = None,
) -> typing.Tuple[Stock, bool]:
    stock = (
        Stock.queryNotSoftDeleted()
        .filter_by(id=stock_id)
        .options(sqla_orm.joinedload(Stock.activationCodes))
        .first_or_404()
    )
    if stock.offerId != offer.id:
        errors = ApiErrors()
        errors.add_error("global", "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information.")
        errors.status_code = 403
        raise errors

    if beginning_datetime is None:
        beginning_datetime = stock.beginningDatetime
    if booking_limit_datetime is None and stock.offer.isEvent:
        booking_limit_datetime = stock.bookingLimitDatetime

    validation.check_booking_limit_datetime(stock, beginning_datetime, booking_limit_datetime)

    # FIXME (dbaty, 2020-11-25): We need this ugly workaround because
    # the frontend sends us datetimes like "2020-12-03T14:00:00Z"
    # (note the "Z" suffix). Pydantic deserializes it as a datetime
    # *with* a timezone. However, datetimes are stored in the database
    # as UTC datetimes *without* any timezone. Thus, we wrongly detect
    # a change for the "beginningDatetime" field for Allocine stocks:
    # because we do not allow it to be changed, we raise an error when
    # we should not.
    if beginning_datetime:
        beginning_datetime = as_utc_without_timezone(beginning_datetime)
    if booking_limit_datetime:
        booking_limit_datetime = as_utc_without_timezone(booking_limit_datetime)

    validation.check_stock_is_updatable(stock, editing_provider)
    validation.check_required_dates_for_stock(stock.offer, beginning_datetime, booking_limit_datetime)
    validation.check_stock_price(price, stock.offer)
    validation.check_stock_quantity(quantity, stock.dnBookedQuantity)
    validation.check_activation_codes_expiration_datetime_on_stock_edition(
        stock.activationCodes,
        booking_limit_datetime,
    )

    is_beginning_updated = beginning_datetime != stock.beginningDatetime

    updates = {
        "price": price,
        "quantity": quantity,
        "beginningDatetime": beginning_datetime,
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

    repository.add_to_session(stock)

    return stock, is_beginning_updated


def handle_stocks_edition(offer_id: int, edited_stocks: list[typing.Tuple[Stock, bool]]) -> None:
    if edited_stocks:
        search.async_index_offer_ids([offer_id])

    for stock, is_beginning_datetime_updated in edited_stocks:
        if is_beginning_datetime_updated:
            bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
            _notify_pro_upon_stock_edit_for_event_offer(stock, bookings)
            _notify_beneficiaries_upon_stock_edit(stock, bookings)


def publish_offer(offer: Offer, user: User | None) -> Offer:
    offer.isActive = True
    update_offer_fraud_information(offer, user)
    search.async_index_offer_ids([offer.id])
    logger.info(  # type: ignore [call-arg]
        "Offer has been published",
        extra={"offer_id": offer.id, "venue_id": offer.venueId, "offer_status": offer.status},
        technical_message_id="offer.published",
    )
    return offer


def update_offer_fraud_information(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate | Offer,
    user: User | None,
    *,
    silent: bool = False,
) -> None:
    venue_already_has_validated_offer = offers_repository.venue_already_has_validated_offer(offer)

    offer.validation = set_offer_status_based_on_fraud_criteria(offer)
    if user is not None:
        offer.author = user
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO

    if offer.validation in (OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED):
        offer.isActive = False

    db.session.add(offer)

    if offer.validation == OfferValidationStatus.APPROVED and not silent:
        admin_emails.send_offer_creation_notification_to_administration(offer)

    if (
        offer.validation == OfferValidationStatus.APPROVED
        and not venue_already_has_validated_offer
        and isinstance(offer, Offer)
    ):
        if not transactional_mails.send_first_venue_approved_offer_email_to_pro(offer):
            logger.warning("Could not send first venue approved offer email", extra={"offer_id": offer.id})


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
            if not transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email(booking):
                logger.warning(
                    "Could not notify beneficiary about deletion of stock",
                    extra={"stock": stock.id, "booking": booking.id},
                )
        if not transactional_mails.send_booking_cancellation_confirmation_by_pro_email(cancelled_bookings):
            logger.warning(
                "Could not notify offerer about deletion of stock",
                extra={"stock": stock.id},
            )

        push_notification_job.send_cancel_booking_notification.delay([booking.id for booking in cancelled_bookings])


def create_mediation(
    user: User | None,
    offer: Offer,
    credit: str | None,
    image_as_bytes: bytes,
    crop_params: image_conversion.CropParams | None = None,
    keep_ratio: bool = False,
    min_width: int = validation.MIN_THUMBNAIL_WIDTH,
    min_height: int = validation.MIN_THUMBNAIL_HEIGHT,
    max_width: int | None = None,
    max_height: int | None = None,
    aspect_ratio: image_conversion.ImageRatio = image_conversion.ImageRatio.PORTRAIT,
) -> Mediation:
    # checks image type, min dimensions
    validation.check_image(
        image_as_bytes, min_width=min_width, min_height=min_height, max_width=max_width, max_height=max_height
    )

    mediation = Mediation(author=user, offer=offer, credit=credit)

    repository.add_to_session(mediation)
    db.session.flush()  # `create_thumb()` requires the object to have an id, so we must flush now.

    try:
        create_thumb(
            mediation,
            image_as_bytes,
            storage_id_suffix_str="",
            crop_params=crop_params,
            ratio=aspect_ratio,
            keep_ratio=keep_ratio,
        )
    except image_conversion.ImageRatioError:
        raise
    except Exception as exception:
        logger.exception("An unexpected error was encountered during the thumbnail creation: %s", exception)
        raise ThumbnailStorageError

    # cleanup former thumbnails and mediations
    previous_mediations = (
        Mediation.query.filter(Mediation.offerId == offer.id).filter(Mediation.id != mediation.id).all()
    )
    _delete_mediations_and_thumbs(previous_mediations)

    search.async_index_offer_ids([offer.id])

    return mediation


def delete_mediation(offer: Offer) -> None:
    mediations = Mediation.query.filter(Mediation.offerId == offer.id).all()

    _delete_mediations_and_thumbs(mediations)

    search.async_index_offer_ids([offer.id])


def _delete_mediations_and_thumbs(mediations: list[Mediation]) -> None:
    for mediation in mediations:
        try:
            for thumb_index in range(1, mediation.thumbCount + 1):
                suffix = str(thumb_index - 1) if thumb_index > 1 else ""
                remove_thumb(mediation, storage_id_suffix=suffix)
        except Exception as exception:  # pylint: disable=broad-except
            logger.exception(
                "An unexpected error was encountered during the thumbnails deletion for %s: %s",
                mediation,
                exception,
            )
        else:
            db.session.delete(mediation)


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

    if stock_ids_already_migrated:
        logger.warning(
            "The following stocks are already migrated from old siret to new siret: [%s]",
            stock_ids_already_migrated,
            extra={"venueId": venue.id, "current_siret": venue.siret, "old_siret": old_siret},
        )

    repository.save(*stocks_to_update)


def get_expense_domains(offer: Offer) -> list[ExpenseDomain]:
    domains = {ExpenseDomain.ALL.value}

    if finance_conf.digital_cap_applies_to_offer(offer):
        domains.add(ExpenseDomain.DIGITAL.value)
    if finance_conf.physical_cap_applies_to_offer(offer):
        domains.add(ExpenseDomain.PHYSICAL.value)

    return list(domains)  # type: ignore [arg-type]


def add_criteria_to_offers(
    criteria: list[criteria_models.Criterion],
    isbn: str | None = None,
    visa: str | None = None,
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


def reject_inappropriate_products(isbn: str) -> bool:
    products = Product.query.filter(Product.extraData["isbn"].astext == isbn).all()
    if not products:
        return False

    for product in products:
        product.isGcuCompatible = False
        db.session.add(product)

    offers = Offer.query.filter(
        Offer.productId.in_(p.id for p in products),
        Offer.validation != OfferValidationStatus.REJECTED,
    )
    offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id).all()]
    offers.update(
        values={
            "validation": OfferValidationStatus.REJECTED,
            "lastValidationDate": datetime.datetime.utcnow(),
            "lastValidationType": OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        },
        synchronize_session="fetch",
    )

    try:
        db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark product and offers as inappropriate: %s",
            extra={"isbn": isbn, "products": [p.id for p in products], "exc": str(exception)},
        )
        return False
    logger.info(
        "Rejected inappropriate products",
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
    offer.validation = validation_status
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
    elif isinstance(offer, educational_models.CollectiveOffer):
        search.async_index_collective_offer_ids([offer.id])
    elif isinstance(offer, educational_models.CollectiveOfferTemplate):
        search.async_index_collective_offer_template_ids([offer.id])
    template = f"{type(offer)} validation status updated"
    logger.info(template, extra={"offer": offer.id, "offer_validation": offer.validation}, technical_message_id="offers.validation_updated")  # type: ignore [call-arg]
    return True


def import_offer_validation_config(config_as_yaml: str, user: User = None) -> OfferValidationConfig:
    try:
        config_as_dict = yaml.safe_load(config_as_yaml)
        validation.check_validation_config_parameters(config_as_dict, validation.KEY_VALIDATION_CONFIG["init"])
    except (KeyError, ValueError, ScannerError) as error:
        logger.exception(
            "Wrong configuration file format: %s",
            error,
            extra={"exc": str(error)},
        )
        raise WrongFormatInFraudConfigurationFile(str(error))  # type: ignore [arg-type]

    config = OfferValidationConfig(specs=config_as_dict, user=user)  # type: ignore [arg-type]
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


def report_offer(user: User, offer: Offer, reason: str, custom_reason: str | None) -> None:
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
            report = OfferReport(user=user, offer=offer, reason=reason, customReasonContent=custom_reason)  # type: ignore [arg-type]
            db.session.add(report)
    except sqla_exc.IntegrityError as error:
        if error.orig.pgcode == UNIQUE_VIOLATION:
            raise OfferAlreadyReportedError() from error
        if error.orig.pgcode == CHECK_VIOLATION:
            raise ReportMalformed() from error
        raise

    if not transactional_mails.send_email_reported_offer_by_user(user, offer, reason, custom_reason):
        logger.warning("Could not send email reported offer by user", extra={"user_id": user.id})


def update_stock_quantity_to_match_cinema_venue_provider_remaining_place(
    offer: Offer, venue_provider: providers_models.VenueProvider
) -> None:
    sentry_sdk.set_tag("cinema-venue-provider", venue_provider.provider.localClass)
    logger.info(
        "Getting up-to-date show stock from booking provider on offer view",
        extra={"offer": offer.id, "venue_provider": venue_provider.id},
    )
    shows_remaining_places = {}
    match venue_provider.provider.localClass:
        case "CDSStocks":
            if not FeatureToggle.ENABLE_CDS_IMPLEMENTATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CDS_IMPLEMENTATION is inactive")
            show_ids = [
                cinema_providers_utils.get_cds_show_id_from_uuid(stock.idAtProviders)
                for stock in offer.activeStocks
                if stock.idAtProviders
            ]
            cleaned_show_ids = [s for s in show_ids if s is not None]
            if not cleaned_show_ids:
                return
            shows_remaining_places = external_bookings_api.get_shows_stock(offer.venueId, cleaned_show_ids)
        case "BoostStocks":
            if not FeatureToggle.ENABLE_BOOST_API_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_BOOST_API_INTEGRATION is inactive")
            film_id = cinema_providers_utils.get_boost_film_id_from_uuid(offer.idAtProvider)
            if not film_id:
                return
            shows_remaining_places = external_bookings_api.get_boost_movie_stocks(offer.venueId, film_id)
        case _:
            raise Exception(f"Unknown Provider: {venue_provider.provider.localClass}")

    for show_id, remaining_places in shows_remaining_places.items():
        stock = next(
            (
                s
                for s in offer.activeStocks
                if cinema_providers_utils.get_showtime_id_from_uuid(s.idAtProviders, venue_provider.provider.localClass)
                == show_id
            )
        )
        if stock and remaining_places <= 0:
            update_stock_quantity_to_dn_booked_quantity(stock.id)


def delete_unwanted_existing_product(isbn: str) -> None:
    product_has_at_least_one_booking = (
        models.Product.query.filter_by(idAtProviders=isbn).join(models.Offer).join(models.Stock).join(Booking).count()
        > 0
    )
    product = (
        models.Product.query.filter(models.Product.can_be_synchronized)
        .filter_by(subcategoryId=subcategories.LIVRE_PAPIER.id)
        .filter_by(idAtProviders=isbn)
        .one_or_none()
    )

    if not product:
        return

    if product_has_at_least_one_booking:
        offers = models.Offer.query.filter_by(productId=product.id)
        offers.update({"isActive": False}, synchronize_session=False)
        db.session.commit()
        product.isGcuCompatible = False
        product.isSynchronizationCompatible = False
        repository.save(product)
        raise exceptions.CannotDeleteProductWithBookings()

    objects_to_delete = []
    objects_to_delete.append(product)
    offers = models.Offer.query.filter_by(productId=product.id).all()
    offer_ids = [offer.id for offer in offers]
    objects_to_delete = objects_to_delete + offers
    stocks = offers_repository.get_stocks_for_offers(offer_ids)
    objects_to_delete = objects_to_delete + stocks
    mediations = models.Mediation.query.filter(models.Mediation.offerId.in_(offer_ids)).all()
    objects_to_delete = objects_to_delete + mediations
    favorites = users_models.Favorite.query.filter(users_models.Favorite.offerId.in_(offer_ids)).all()
    objects_to_delete = objects_to_delete + favorites
    repository.delete(*objects_to_delete)


def batch_delete_draft_offers(query: BaseQuery) -> None:
    offer_ids = [id_ for id_, in query.with_entities(Offer.id)]
    filters = (Offer.validation == OfferValidationStatus.DRAFT, Offer.id.in_(offer_ids))
    Mediation.query.filter(Mediation.offerId == Offer.id).filter(*filters).delete(synchronize_session=False)
    criteria_models.OfferCriterion.query.filter(
        criteria_models.OfferCriterion.offerId == Offer.id,
        *filters,
    ).delete(synchronize_session=False)
    ActivationCode.query.filter(
        ActivationCode.stockId == Stock.id,
        Stock.offerId == Offer.id,
        *filters,
    ).delete(synchronize_session=False)
    Stock.query.filter(Stock.offerId == Offer.id).filter(*filters).delete(synchronize_session=False)
    Offer.query.filter(*filters).delete(synchronize_session=False)
    db.session.commit()
