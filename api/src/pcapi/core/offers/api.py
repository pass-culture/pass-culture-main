import datetime
import decimal
import enum
import logging
import typing

from flask_sqlalchemy import BaseQuery
from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
import sentry_sdk
import sqlalchemy.exc as sqla_exc
from werkzeug.exceptions import BadRequest
import yaml
from yaml.scanner import ScannerError

from pcapi import settings
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import remove_thumb
from pcapi.core import search
import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.categories import subcategories
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import validation as educational_validation
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.external.attributes.api import update_external_pro
import pcapi.core.external_bookings.api as external_bookings_api
import pcapi.core.finance.conf as finance_conf
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.models import db
from pcapi.models import feature
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.utils import image_conversion
import pcapi.utils.cinema_providers as cinema_providers_utils
from pcapi.utils.custom_logic import OPERATIONS
from pcapi.workers import push_notification_job

from . import exceptions
from . import models
from . import offer_validation
from . import repository as offers_repository
from . import validation


logger = logging.getLogger(__name__)

AnyOffer = educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate | models.Offer

OFFERS_RECAP_LIMIT = 501


OFFER_LIKE_MODELS = {
    "Offer",
    "CollectiveOffer",
    "CollectiveOfferTemplate",
}


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN


def list_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    category_id: str | None,
    offerer_id: int | None,
    venue_id: int | None = None,
    name_keywords_or_ean: str | None = None,
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
        name_keywords_or_ean=name_keywords_or_ean,
        creation_mode=creation_mode,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
    )


def build_new_offer_from_product(
    venue: offerers_models.Venue,
    product: models.Product,
    id_at_provider: str | None,
    provider_id: int | None,
) -> models.Offer:
    return models.Offer(
        bookingEmail=venue.bookingEmail,
        description=product.description,
        extraData=product.extraData,
        idAtProvider=id_at_provider,
        lastProviderId=provider_id,
        name=product.name,
        productId=product.id,
        venueId=venue.id,
        subcategoryId=product.subcategoryId,
        withdrawalDetails=venue.withdrawalDetails,
    )


def _format_extra_data(subcategory_id: str, extra_data: dict[str, typing.Any] | None) -> models.OfferExtraData | None:
    """Keep only the fields that are defined in the subcategory conditional fields"""
    if extra_data is None:
        return None

    formatted_extra_data: models.OfferExtraData = {}

    for field_name in subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id].conditional_fields.keys():
        if extra_data.get(field_name):
            # FIXME (2023-03-16): Currently not supported by mypy https://github.com/python/mypy/issues/7178
            formatted_extra_data[field_name] = extra_data.get(field_name)  # type: ignore[literal-required]

    return formatted_extra_data


def create_offer(
    audio_disability_compliant: bool,
    mental_disability_compliant: bool,
    motor_disability_compliant: bool,
    name: str,
    subcategory_id: str,
    venue: offerers_models.Venue,
    visual_disability_compliant: bool,
    booking_email: str | None = None,
    description: str | None = None,
    duration_minutes: int | None = None,
    external_ticket_office_url: str | None = None,
    extra_data: dict | None = None,
    is_duo: bool | None = None,
    is_national: bool | None = None,
    provider: providers_models.Provider | None = None,
    url: str | None = None,
    withdrawal_delay: int | None = None,
    withdrawal_details: str | None = None,
    withdrawal_type: models.WithdrawalTypeEnum | None = None,
) -> models.Offer:
    validation.check_offer_withdrawal(withdrawal_type, withdrawal_delay, subcategory_id)
    validation.check_offer_subcategory_is_valid(subcategory_id)
    formatted_extra_data = _format_extra_data(subcategory_id, extra_data)
    validation.check_offer_extra_data(subcategory_id, formatted_extra_data, venue)
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id]
    validation.check_is_duo_compliance(is_duo, subcategory)

    if should_retrieve_book_from_isbn(subcategory.id):
        product = _load_product_by_isbn(formatted_extra_data.get("isbn") if formatted_extra_data else None)
        is_national = bool(is_national) if is_national is not None else product.isNational
    else:
        is_national = True if url else bool(is_national)
        product = models.Product(
            name=name,
            description=description,
            url=url,
            durationMinutes=duration_minutes,
            isNational=is_national,
            owningOfferer=venue.managingOfferer,
            subcategoryId=subcategory_id,
        )

    offer = models.Offer(
        ageMin=product.ageMin,
        ageMax=product.ageMax,
        audioDisabilityCompliant=audio_disability_compliant,
        bookingEmail=booking_email,
        conditions=product.conditions,
        description=product.description or description,
        durationMinutes=duration_minutes,
        externalTicketOfficeUrl=external_ticket_office_url,
        extraData=(product.extraData or {}) | (formatted_extra_data or {}),
        isActive=False,
        isDuo=bool(is_duo),
        isNational=is_national,
        mentalDisabilityCompliant=mental_disability_compliant,
        motorDisabilityCompliant=motor_disability_compliant,
        lastProvider=provider,
        subcategoryId=product.subcategoryId,
        name=name,
        product=product,
        url=url,
        validation=models.OfferValidationStatus.DRAFT,
        venue=venue,
        visualDisabilityCompliant=visual_disability_compliant,
        withdrawalDelay=withdrawal_delay,
        withdrawalDetails=withdrawal_details,
        withdrawalType=withdrawal_type,
    )

    repository.add_to_session(offer)

    logger.info(
        "models.Offer has been created",
        extra={"offer_id": offer.id, "venue_id": venue.id, "product_id": offer.productId},
        technical_message_id="offer.created",
    )

    update_external_pro(venue.bookingEmail)

    return offer


def should_retrieve_book_from_isbn(subcategory_id: str) -> bool:
    return (
        subcategory_id == subcategories.LIVRE_PAPIER.id
        and FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION.is_active()
    )


def update_offer(
    offer: models.Offer,
    ageMax: int | None | T_UNCHANGED = UNCHANGED,
    ageMin: int | None | T_UNCHANGED = UNCHANGED,
    audioDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    bookingEmail: str | None | T_UNCHANGED = UNCHANGED,
    conditions: str | None | T_UNCHANGED = UNCHANGED,
    description: str | None | T_UNCHANGED = UNCHANGED,
    durationMinutes: int | None | T_UNCHANGED = UNCHANGED,
    externalTicketOfficeUrl: str | None | T_UNCHANGED = UNCHANGED,
    extraData: dict | None | T_UNCHANGED = UNCHANGED,
    isActive: bool | T_UNCHANGED = UNCHANGED,
    isDuo: bool | T_UNCHANGED = UNCHANGED,
    isNational: bool | T_UNCHANGED = UNCHANGED,
    mediaUrls: list[str] | None | T_UNCHANGED = UNCHANGED,
    mentalDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    motorDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    name: str | T_UNCHANGED = UNCHANGED,
    url: str | None | T_UNCHANGED = UNCHANGED,
    visualDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    withdrawalDelay: int | None | T_UNCHANGED = UNCHANGED,
    withdrawalDetails: str | None | T_UNCHANGED = UNCHANGED,
    withdrawalType: models.WithdrawalTypeEnum | None | T_UNCHANGED = UNCHANGED,
    shouldSendMail: bool = False,
) -> models.Offer:
    modifications = {
        field: new_value
        for field, new_value in locals().items()
        if field not in ("offer", "shouldSendMail")
        and new_value is not UNCHANGED  # has the user provided a value for this field
        and getattr(offer, field) != new_value  # is the value different from what we have on database?
    }
    if not modifications:
        return offer

    validation.check_validation_status(offer)
    if extraData is not UNCHANGED:
        formatted_extra_data = _format_extra_data(offer.subcategoryId, extraData)
        validation.check_offer_extra_data(offer.subcategoryId, formatted_extra_data, offer.venue)
    if isDuo is not UNCHANGED:
        validation.check_is_duo_compliance(isDuo, offer.subcategory)

    withdrawal_updated = not (
        withdrawalType is UNCHANGED and withdrawalDelay is UNCHANGED and withdrawalDetails is UNCHANGED
    )
    if withdrawal_updated:
        changed_withdrawalType = offer.withdrawalType if withdrawalType is UNCHANGED else withdrawalType
        changed_withdrawalDelay = offer.withdrawalDelay if withdrawalDelay is UNCHANGED else withdrawalDelay

        if not (withdrawalType is UNCHANGED and withdrawalDelay is UNCHANGED):
            validation.check_offer_withdrawal(changed_withdrawalType, changed_withdrawalDelay, offer.subcategoryId)

    if offer.isFromProvider:
        validation.check_update_only_allowed_fields_for_offer_from_provider(set(modifications), offer.lastProvider)

    offer.populate_from_dict(modifications)
    if offer.isFromAllocine:
        offer.fieldsUpdated = list(set(offer.fieldsUpdated) | set(modifications))

    repository.add_to_session(offer)

    if offer.product.owningOfferer and offer.product.owningOfferer == offer.venue.managingOfferer:
        offer.product.populate_from_dict(modifications)
        repository.add_to_session(offer.product)
        product_has_been_updated = True
    else:
        product_has_been_updated = False

    logger.info("Offer has been updated", extra={"offer_id": offer.id}, technical_message_id="offer.updated")
    if product_has_been_updated:
        logger.info("Product has been updated", extra={"product": offer.product.id})

    if shouldSendMail and withdrawal_updated and FeatureToggle.WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL.is_active():
        transactional_mails.send_email_for_each_ongoing_booking(offer)

    search.async_index_offer_ids([offer.id])

    return offer


def update_collective_offer(
    offer_id: int,
    new_values: dict,
) -> None:
    offer_to_update = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id == offer_id
    ).first()
    educational_validation.check_if_offer_is_not_public_api(offer_to_update)
    educational_validation.check_if_offer_not_used_or_reimbursed(offer_to_update)
    if "students" in new_values:
        # FIXME remove after 2023-09-01
        stock = offer_to_update.collectiveStock
        if stock and stock.beginningDatetime < datetime.datetime(2023, 9, 1):
            new_students = []
            for student in new_values["students"]:
                if student in (educational_models.StudentLevels.COLLEGE5, educational_models.StudentLevels.COLLEGE6):
                    continue
                new_students.append(student)
            if new_students:
                new_values["students"] = new_students
            else:
                raise educational_exceptions.StudentsNotOpenedYet()

    if "venueId" in new_values and new_values["venueId"] != offer_to_update.venueId:
        offerer = offerers_repository.get_by_collective_offer_id(offer_to_update.id)
        new_venue = offerers_api.get_venue_by_id(new_values["venueId"])
        if not new_venue:
            raise educational_exceptions.VenueIdDontExist()
        if new_venue.managingOffererId != offerer.id:
            raise educational_exceptions.OffererOfVenueDontMatchOfferer()
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

    if "venueId" in new_values and new_values["venueId"] != offer_to_update.venueId:
        new_venue = offerers_api.get_venue_by_id(new_values["venueId"])
        if not new_venue:
            raise educational_exceptions.VenueIdDontExist()
        offerer = offerers_repository.get_by_collective_offer_template_id(offer_to_update.id)
        if new_venue.managingOffererId != offerer.id:
            raise educational_exceptions.OffererOfVenueDontMatchOfferer()
    _update_collective_offer(offer=offer_to_update, new_values=new_values)
    search.async_index_collective_offer_template_ids([offer_to_update.id])


def _update_collective_offer(offer: AnyOffer, new_values: dict) -> list[str]:
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


def batch_update_offers(query: BaseQuery, update_fields: dict, send_email_notification: bool = False) -> None:
    query = query.filter(models.Offer.validation == models.OfferValidationStatus.APPROVED)
    raw_results = query.with_entities(models.Offer.id, models.Offer.venueId).all()
    offer_ids, venue_ids = [], []
    if raw_results:
        offer_ids, venue_ids = zip(*raw_results)
    venue_ids = sorted(set(venue_ids))
    number_of_offers_to_update = len(offer_ids)
    logger.info(
        "Batch update of offers",
        extra={"updated_fields": update_fields, "nb_offers": number_of_offers_to_update, "venue_ids": venue_ids},
    )
    if "isActive" in update_fields.keys():
        message = "Offers has been activated" if update_fields["isActive"] else "Offers has been deactivated"
        technical_message_id = "offers.activated" if update_fields["isActive"] else "offers.deactivated"
        logger.info(
            message,
            extra={"offer_ids": offer_ids, "venue_id": venue_ids},
            technical_message_id=technical_message_id,
        )

    batch_size = 1000
    for current_start_index in range(0, number_of_offers_to_update, batch_size):
        offer_ids_batch = offer_ids[
            current_start_index : min(current_start_index + batch_size, number_of_offers_to_update)
        ]

        query_to_update = models.Offer.query.filter(models.Offer.id.in_(offer_ids_batch))
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.commit()

        search.async_index_offer_ids(offer_ids_batch)

        withdrawal_updated = {"withdrawalDetails", "withdrawalType", "withdrawalDelay"}.intersection(
            update_fields.keys()
        )
        if (
            send_email_notification
            and withdrawal_updated
            and FeatureToggle.WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL.is_active()
        ):
            for offer in query_to_update.all():
                transactional_mails.send_email_for_each_ongoing_booking(offer)


def batch_update_collective_offers(query: BaseQuery, update_fields: dict) -> None:
    collective_offer_ids_tuples = query.filter(
        educational_models.CollectiveOffer.validation == models.OfferValidationStatus.APPROVED
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


def batch_update_collective_offers_template(query: BaseQuery, update_fields: dict) -> None:
    collective_offer_ids_tuples = query.filter(
        educational_models.CollectiveOfferTemplate.validation == models.OfferValidationStatus.APPROVED
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


def _notify_pro_upon_stock_edit_for_event_offer(
    stock: models.Stock, bookings: typing.List[bookings_models.Booking]
) -> None:
    if stock.offer.isEvent:
        if not transactional_mails.send_event_offer_postponement_confirmation_email_to_pro(stock, len(bookings)):
            logger.warning(
                "Could not notify pro about update of stock concerning an event offer",
                extra={"stock": stock.id},
            )


def _notify_beneficiaries_upon_stock_edit(stock: models.Stock, bookings: typing.List[bookings_models.Booking]) -> None:
    if bookings:
        if stock.beginningDatetime is None:
            logger.error(
                "Could not notify beneficiaries about update of stock. No beginningDatetime in stock.",
                extra={"stock": stock.id},
            )
            return
        bookings = bookings_api.update_cancellation_limit_dates(bookings, stock.beginningDatetime)
        date_in_two_days = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        check_event_is_in_more_than_48_hours = stock.beginningDatetime > date_in_two_days
        if check_event_is_in_more_than_48_hours:
            bookings = _invalidate_bookings(bookings)
        if not transactional_mails.send_batch_booking_postponement_email_to_users(bookings):
            logger.warning(
                "Could not notify beneficiaries about update of stock",
                extra={"stock": stock.id},
            )


def create_stock(
    offer: models.Offer,
    quantity: int | None,
    activation_codes: list[str] | None = None,
    activation_codes_expiration_datetime: datetime.datetime | None = None,
    beginning_datetime: datetime.datetime | None = None,
    booking_limit_datetime: datetime.datetime | None = None,
    creating_provider: providers_models.Provider | None = None,
    price: decimal.Decimal | None = None,
    price_category: models.PriceCategory | None = None,
) -> models.Stock:
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

    if price is None:
        if price_category:
            price = price_category.price
        else:
            # This should never happen
            raise BadRequest()

    validation.check_required_dates_for_stock(offer, beginning_datetime, booking_limit_datetime)
    validation.check_validation_status(offer)
    validation.check_provider_can_create_stock(offer, creating_provider)
    validation.check_stock_price(price, offer)
    validation.check_stock_quantity(quantity)

    created_stock = models.Stock(
        offerId=offer.id,
        price=price,
        quantity=quantity,
        beginningDatetime=beginning_datetime,
        bookingLimitDatetime=booking_limit_datetime,
        priceCategory=price_category,  # type: ignore [arg-type]
    )
    created_activation_codes = []

    for activation_code in activation_codes:
        created_activation_codes.append(
            models.ActivationCode(
                code=activation_code,
                expirationDate=activation_codes_expiration_datetime,
                stock=created_stock,
            )
        )
    repository.add_to_session(created_stock, *created_activation_codes)
    search.async_index_offer_ids([offer.id])

    return created_stock


def edit_stock(
    stock: models.Stock,
    price: decimal.Decimal | None | T_UNCHANGED = UNCHANGED,
    quantity: int | None | T_UNCHANGED = UNCHANGED,
    beginning_datetime: datetime.datetime | None | T_UNCHANGED = UNCHANGED,
    booking_limit_datetime: datetime.datetime | None | T_UNCHANGED = UNCHANGED,
    editing_provider: providers_models.Provider | None = None,
    price_category: models.PriceCategory | None | T_UNCHANGED = UNCHANGED,
) -> typing.Tuple[models.Stock, bool]:
    validation.check_stock_is_updatable(stock, editing_provider)

    modifications: dict[str, typing.Any] = {}

    if beginning_datetime is not UNCHANGED or booking_limit_datetime is not UNCHANGED:
        changed_beginning = beginning_datetime if beginning_datetime is not UNCHANGED else stock.beginningDatetime
        changed_booking_limit = (
            booking_limit_datetime if booking_limit_datetime is not UNCHANGED else stock.bookingLimitDatetime
        )
        validation.check_booking_limit_datetime(stock, changed_beginning, changed_booking_limit)
        validation.check_required_dates_for_stock(stock.offer, changed_beginning, changed_booking_limit)

    if price is not UNCHANGED and price is not None and price != stock.price:
        modifications["price"] = price
        validation.check_stock_price(price, stock.offer)

    if price_category is not UNCHANGED and price_category is not None and price_category is not stock.priceCategory:
        modifications["priceCategory"] = price_category
        modifications["price"] = price_category.price

    if quantity is not UNCHANGED and quantity != stock.quantity:
        modifications["quantity"] = quantity
        validation.check_stock_quantity(quantity, stock.dnBookedQuantity)

    if booking_limit_datetime is not UNCHANGED and booking_limit_datetime != stock.bookingLimitDatetime:
        modifications["bookingLimitDatetime"] = booking_limit_datetime
        validation.check_activation_codes_expiration_datetime_on_stock_edition(
            stock.activationCodes,
            booking_limit_datetime,
        )

    is_beginning_updated = False
    if beginning_datetime not in (UNCHANGED, stock.beginningDatetime):
        modifications["beginningDatetime"] = beginning_datetime
        is_beginning_updated = True

    if stock.offer.isFromAllocine:
        updated_fields = set(modifications)
        validation.check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields)
        stock.fieldsUpdated = list(set(stock.fieldsUpdated) | updated_fields)

    for model_attr, value in modifications.items():
        setattr(stock, model_attr, value)

    repository.add_to_session(stock)
    search.async_index_offer_ids([stock.offerId])

    return stock, is_beginning_updated


def handle_stocks_edition(offer_id: int, edited_stocks: list[typing.Tuple[models.Stock, bool]]) -> None:
    for stock, is_beginning_datetime_updated in edited_stocks:
        if is_beginning_datetime_updated:
            bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
            _notify_pro_upon_stock_edit_for_event_offer(stock, bookings)
            _notify_beneficiaries_upon_stock_edit(stock, bookings)


def publish_offer(offer: models.Offer, user: users_models.User | None) -> models.Offer:
    offer.isActive = True
    update_offer_fraud_information(offer, user)
    search.async_index_offer_ids([offer.id])
    logger.info(
        "Offer has been published",
        extra={"offer_id": offer.id, "venue_id": offer.venueId, "offer_status": offer.status},
        technical_message_id="offer.published",
    )
    return offer


def update_offer_fraud_information(offer: AnyOffer, user: users_models.User | None) -> None:
    venue_already_has_validated_offer = offers_repository.venue_already_has_validated_offer(offer)

    if feature.FeatureToggle.WIP_ENABLE_NEW_FRAUD_RULES.is_active():
        offer.validation = set_offer_status_based_on_fraud_criteria_v2(offer)
    else:
        offer.validation = set_offer_status_based_on_fraud_criteria(offer)
    if user is not None:
        offer.author = user
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO

    if offer.validation in (models.OfferValidationStatus.PENDING, models.OfferValidationStatus.REJECTED):
        offer.isActive = False

    db.session.add(offer)

    if (
        offer.validation == models.OfferValidationStatus.APPROVED
        and not venue_already_has_validated_offer
        and isinstance(offer, models.Offer)
    ):
        if not transactional_mails.send_first_venue_approved_offer_email_to_pro(offer):
            logger.warning("Could not send first venue approved offer email", extra={"offer_id": offer.id})


def _invalidate_bookings(bookings: list[bookings_models.Booking]) -> list[bookings_models.Booking]:
    for booking in bookings:
        if booking.status is bookings_models.BookingStatus.USED:
            bookings_api.mark_as_unused(booking)
    return bookings


def delete_stock(stock: models.Stock) -> None:
    validation.check_stock_is_deletable(stock)

    stock.isSoftDeleted = True
    repository.save(stock)

    # the algolia sync for the stock will happen within this function
    cancelled_bookings = bookings_api.cancel_bookings_from_stock_by_offerer(stock)

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
    user: users_models.User | None,
    offer: models.Offer,
    credit: str | None,
    image_as_bytes: bytes,
    crop_params: image_conversion.CropParams | None = None,
    keep_ratio: bool = False,
    min_width: int = validation.MIN_THUMBNAIL_WIDTH,
    min_height: int = validation.MIN_THUMBNAIL_HEIGHT,
    max_width: int | None = None,
    max_height: int | None = None,
    aspect_ratio: image_conversion.ImageRatio = image_conversion.ImageRatio.PORTRAIT,
) -> models.Mediation:
    # checks image type, min dimensions
    validation.check_image(
        image_as_bytes, min_width=min_width, min_height=min_height, max_width=max_width, max_height=max_height
    )

    mediation = models.Mediation(author=user, offer=offer, credit=credit)

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
        raise exceptions.ThumbnailStorageError

    # cleanup former thumbnails and mediations
    previous_mediations = (
        models.Mediation.query.filter(models.Mediation.offerId == offer.id)
        .filter(models.Mediation.id != mediation.id)
        .all()
    )
    _delete_mediations_and_thumbs(previous_mediations)

    search.async_index_offer_ids([offer.id])

    return mediation


def delete_mediation(offer: models.Offer) -> None:
    mediations = models.Mediation.query.filter(models.Mediation.offerId == offer.id).all()

    _delete_mediations_and_thumbs(mediations)

    search.async_index_offer_ids([offer.id])


def _delete_mediations_and_thumbs(mediations: list[models.Mediation]) -> None:
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


def update_stock_id_at_providers(venue: offerers_models.Venue, old_siret: str) -> None:
    current_siret = venue.siret

    stocks = (
        models.Stock.query.join(models.Offer)
        .filter(models.Offer.venueId == venue.id)
        .filter(models.Stock.idAtProviders.endswith(old_siret))
        .all()
    )

    stock_ids_already_migrated = []
    stocks_to_update = []

    for stock in stocks:
        new_id_at_providers = stock.idAtProviders.replace(old_siret, current_siret)
        if db.session.query(models.Stock.query.filter_by(idAtProviders=new_id_at_providers).exists()).scalar():
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


def get_expense_domains(offer: models.Offer) -> list[users_models.ExpenseDomain]:
    domains = {users_models.ExpenseDomain.ALL}

    if finance_conf.digital_cap_applies_to_offer(offer):
        domains.add(users_models.ExpenseDomain.DIGITAL)
    if finance_conf.physical_cap_applies_to_offer(offer):
        domains.add(users_models.ExpenseDomain.PHYSICAL)

    return list(domains)


def add_criteria_to_offers(
    criterion_ids: list[int],
    ean: str | None = None,
    visa: str | None = None,
) -> bool:
    if not ean and not visa:
        return False

    query = models.Product.query
    if ean:
        ean = ean.replace("-", "").replace(" ", "")
        query = query.filter(models.Product.extraData["ean"].astext == ean)
    if visa:
        query = query.filter(models.Product.extraData["visa"].astext == visa)

    products = query.all()
    if not products:
        return False

    offer_ids_query = models.Offer.query.filter(
        models.Offer.productId.in_(p.id for p in products), models.Offer.isActive.is_(True)
    ).with_entities(models.Offer.id)
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
    for criterion_id in criterion_ids:
        logger.info("Adding criterion %s to %d offers", criterion_id, len(offer_ids))
        for offer_id in offer_ids:
            if not (offer_id, criterion_id) in existing_criteria_on_offers:
                offer_criteria.append(
                    criteria_models.OfferCriterion(
                        offerId=offer_id,
                        criterionId=criterion_id,
                    )
                )

    db.session.bulk_save_objects(offer_criteria)
    db.session.commit()

    search.async_index_offer_ids(offer_ids)

    return True


def reject_inappropriate_products(ean: str) -> bool:
    products = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).all()
    if not products:
        return False

    for product in products:
        product.isGcuCompatible = False
        db.session.add(product)

    offers = models.Offer.query.filter(
        models.Offer.productId.in_(p.id for p in products),
        models.Offer.validation != models.OfferValidationStatus.REJECTED,
    )
    offer_ids = [offer_id for offer_id, in offers.with_entities(models.Offer.id).all()]
    offers.update(
        values={
            "validation": models.OfferValidationStatus.REJECTED,
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
            extra={"isbn": ean, "products": [p.id for p in products], "exc": str(exception)},
        )
        return False
    logger.info(
        "Rejected inappropriate products",
        extra={"isbn": ean, "products": [p.id for p in products], "offers": offer_ids},
    )

    search.async_index_offer_ids(offer_ids)

    return True


def deactivate_permanently_unavailable_products(ean: str) -> bool:
    products = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).all()
    if not products:
        return False

    for product in products:
        product.name = "xxx"
        db.session.add(product)

    offers = models.Offer.query.filter(models.Offer.productId.in_(p.id for p in products)).filter(
        models.Offer.isActive.is_(True)
    )
    offer_ids = [offer_id for offer_id, in offers.with_entities(models.Offer.id).all()]
    offers.update(values={"isActive": False, "name": "xxx"}, synchronize_session="fetch")

    try:
        db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark product and offers as permanently unavailable: %s",
            extra={"ean": ean, "products": [p.id for p in products], "exc": str(exception)},
        )
        return False
    logger.info(
        "Deactivated permanently unavailable products",
        extra={"isbn": ean, "products": [p.id for p in products], "offers": offer_ids},
    )

    search.async_index_offer_ids(offer_ids)

    return True


def set_offer_status_based_on_fraud_criteria(offer: AnyOffer) -> models.OfferValidationStatus:
    current_config = offers_repository.get_current_offer_validation_config()
    if not current_config:
        return models.OfferValidationStatus.APPROVED

    minimum_score, validation_rules = offer_validation.parse_offer_validation_config(offer, current_config)

    score = offer_validation.compute_offer_validation_score(validation_rules)
    if score < minimum_score:
        status = models.OfferValidationStatus.PENDING
    else:
        status = models.OfferValidationStatus.APPROVED

    logger.info("Computed offer validation", extra={"offer": offer.id, "score": score, "status": status.value})
    return status


def resolve_offer_validation_sub_rule(sub_rule: models.OfferValidationSubRule, offer: AnyOffer) -> bool:
    if sub_rule.model:
        if sub_rule.model.value in OFFER_LIKE_MODELS and type(offer).__name__ == sub_rule.model.value:
            object_to_compare = offer
        elif sub_rule.model.value == "CollectiveStock" and isinstance(offer, educational_models.CollectiveOffer):
            object_to_compare = offer.collectiveStock
        elif sub_rule.model.value == "Venue":
            object_to_compare = offer.venue
        elif sub_rule.model.value == "Offerer":
            object_to_compare = offer.venue.managingOfferer
        else:
            raise exceptions.UnapplicableModel()

        target_attribute = getattr(object_to_compare, sub_rule.attribute.value)
    else:
        target_attribute = type(offer).__name__

    return OPERATIONS[sub_rule.operator.value](target_attribute, sub_rule.comparated["comparated"])  # type: ignore[operator]


def rule_flags_offer(rule: models.OfferValidationRule, offer: AnyOffer) -> bool:
    is_offer_flagged = all(resolve_offer_validation_sub_rule(sub_rule, offer) for sub_rule in rule.subRules)
    return is_offer_flagged


def set_offer_status_based_on_fraud_criteria_v2(offer: AnyOffer) -> models.OfferValidationStatus:
    offer_validation_rules = models.OfferValidationRule.query.all()

    flagging_rules = dict()
    for rule in offer_validation_rules:
        if rule_flags_offer(rule, offer):
            flagging_rules[rule.id] = rule.name

    if flagging_rules:
        status = models.OfferValidationStatus.PENDING
    else:
        status = models.OfferValidationStatus.APPROVED

    logger.info("Computed offer validation", extra={"offer": offer.id, "status": status.value})
    return status


def update_pending_offer_validation(offer: models.Offer, validation_status: models.OfferValidationStatus) -> bool:
    offer = type(offer).query.filter_by(id=offer.id).one()
    if offer.validation != models.OfferValidationStatus.PENDING:
        template = f"{type(offer)} validation status cannot be updated, initial validation status is not PENDING. %s"
        logger.info(template, extra={"offer": offer.id})
        return False
    offer.validation = validation_status
    if validation_status == models.OfferValidationStatus.APPROVED:
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
    if isinstance(offer, models.Offer):
        search.async_index_offer_ids([offer.id])
    elif isinstance(offer, educational_models.CollectiveOffer):
        search.async_index_collective_offer_ids([offer.id])
    elif isinstance(offer, educational_models.CollectiveOfferTemplate):
        search.async_index_collective_offer_template_ids([offer.id])
    template = f"{type(offer)} validation status updated"
    logger.info(
        template,
        extra={"offer": offer.id, "offer_validation": offer.validation},
        technical_message_id="offers.validation_updated",
    )
    return True


def import_offer_validation_config(config_as_yaml: str, user: users_models.User) -> models.OfferValidationConfig:
    try:
        config_as_dict = yaml.safe_load(config_as_yaml)
        validation.check_validation_config_parameters(config_as_dict, validation.KEY_VALIDATION_CONFIG["init"])
    except (KeyError, ValueError, ScannerError) as error:
        logger.exception(
            "Wrong configuration file format: %s",
            error,
            extra={"exc": str(error)},
        )
        raise exceptions.WrongFormatInFraudConfigurationFile(error)

    config = models.OfferValidationConfig(specs=config_as_dict, user=user)
    repository.save(config)
    return config


def _load_product_by_isbn(isbn: str | None) -> models.Product:
    if not isbn:
        raise exceptions.MissingEAN()
    product = models.Product.query.filter(models.Product.extraData["isbn"].astext == isbn).first()
    if product is None or not product.isGcuCompatible:
        raise exceptions.NotEligibleEAN()
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
        offer_ids = [offer_id for offer_id, in offers.with_entities(models.Offer.id)]

        if not offer_ids:
            break

        logger.info("[ALGOLIA] Found %d expired offers to unindex", len(offer_ids))
        search.unindex_offer_ids(offer_ids)
        page += 1


def report_offer(
    user: users_models.User, offer: models.Offer, reason: models.Reason, custom_reason: str | None
) -> None:
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
            report = models.OfferReport(user=user, offer=offer, reason=reason, customReasonContent=custom_reason)
            db.session.add(report)
    except sqla_exc.IntegrityError as error:
        if error.orig.pgcode == UNIQUE_VIOLATION:
            raise exceptions.OfferAlreadyReportedError() from error
        if error.orig.pgcode == CHECK_VIOLATION:
            raise exceptions.ReportMalformed() from error
        raise

    if not transactional_mails.send_email_reported_offer_by_user(user, offer, reason, custom_reason):
        logger.warning("Could not send email reported offer by user", extra={"user_id": user.id})


def update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer: models.Offer) -> None:
    try:
        venue_provider = external_bookings_api.get_active_cinema_venue_provider(offer.venueId)
        validation.check_offer_is_from_current_cinema_provider(offer)
    except (exceptions.UnexpectedCinemaProvider, providers_exceptions.InactiveProvider):
        offer.isActive = False
        repository.save(offer)
        search.async_index_offer_ids([offer.id])
        return

    sentry_sdk.set_tag("cinema-venue-provider", venue_provider.provider.localClass)
    logger.info(
        "Getting up-to-date show stock from booking provider on offer view",
        extra={"offer": offer.id, "venue_provider": venue_provider.id},
    )
    offer_current_stocks = offer.bookableStocks

    match venue_provider.provider.localClass:
        case "CDSStocks":
            if not FeatureToggle.ENABLE_CDS_IMPLEMENTATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CDS_IMPLEMENTATION is inactive")
            show_ids = [
                cinema_providers_utils.get_cds_show_id_from_uuid(stock.idAtProviders)
                for stock in offer.bookableStocks
                if stock.idAtProviders
            ]
            cleaned_show_ids = [s for s in show_ids if s is not None]
            if not cleaned_show_ids:
                return
            shows_remaining_places = external_bookings_api.get_shows_stock(offer.venueId, cleaned_show_ids)
        case "BoostStocks":
            if not FeatureToggle.ENABLE_BOOST_API_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_BOOST_API_INTEGRATION is inactive")
            film_id = cinema_providers_utils.get_boost_or_cgr_film_id_from_uuid(offer.idAtProvider)
            if not film_id:
                return
            shows_remaining_places = external_bookings_api.get_movie_stocks(offer.venueId, film_id)
        case "CGRStocks":
            if not FeatureToggle.ENABLE_CGR_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CGR_INTEGRATION is inactive")
            cgr_allocine_film_id = cinema_providers_utils.get_boost_or_cgr_film_id_from_uuid(offer.idAtProvider)
            if not cgr_allocine_film_id:
                return
            shows_remaining_places = external_bookings_api.get_movie_stocks(offer.venueId, cgr_allocine_film_id)
        case _:
            raise ValueError(f"Unknown Provider: {venue_provider.provider.localClass}")

    offer_has_new_sold_out_stock = False
    for stock in offer_current_stocks:
        showtime_id = cinema_providers_utils.get_showtime_id_from_uuid(
            stock.idAtProviders, venue_provider.provider.localClass
        )
        assert showtime_id
        remaining_places = shows_remaining_places.pop(showtime_id, None)
        # make this stock sold out, instead of soft-deleting it (don't update its bookings)
        if remaining_places is None or remaining_places <= 0:
            try:
                offers_repository.update_stock_quantity_to_dn_booked_quantity(stock.id)
            except sqla_exc.InternalError:
                # The SQLAlchemy session is invalidated as soon as an InternalError is raised
                db.session.rollback()
                bookings_api.recompute_dnBookedQuantity([stock.id])
                offers_repository.update_stock_quantity_to_dn_booked_quantity(stock.id)
            offer_has_new_sold_out_stock = True
        # to prevent a duo booking to fail
        if remaining_places == 1:
            stock.quantity = stock.dnBookedQuantity + 1
            repository.save(stock)

    if offer_has_new_sold_out_stock:
        search.async_index_offer_ids([offer.id])


def delete_unwanted_existing_product(idAtProviders: str) -> None:
    product_has_at_least_one_booking = (
        models.Product.query.filter_by(idAtProviders=idAtProviders)
        .join(models.Offer)
        .join(models.Stock)
        .join(bookings_models.Booking)
        .count()
        > 0
    )
    product = (
        models.Product.query.filter(models.Product.can_be_synchronized)
        .filter_by(subcategoryId=subcategories.LIVRE_PAPIER.id)
        .filter_by(idAtProviders=idAtProviders)
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
    offer_ids = [id_ for id_, in query.with_entities(models.Offer.id)]
    filters = (models.Offer.validation == models.OfferValidationStatus.DRAFT, models.Offer.id.in_(offer_ids))
    models.Mediation.query.filter(models.Mediation.offerId == models.Offer.id).filter(*filters).delete(
        synchronize_session=False
    )
    criteria_models.OfferCriterion.query.filter(
        criteria_models.OfferCriterion.offerId == models.Offer.id,
        *filters,
    ).delete(synchronize_session=False)
    models.ActivationCode.query.filter(
        models.ActivationCode.stockId == models.Stock.id,
        models.Stock.offerId == models.Offer.id,
        *filters,
    ).delete(synchronize_session=False)
    models.Stock.query.filter(models.Stock.offerId == models.Offer.id).filter(*filters).delete(
        synchronize_session=False
    )
    models.Offer.query.filter(*filters).delete(synchronize_session=False)
    db.session.commit()


def get_or_create_label(label: str, venue: offerers_models.Venue) -> models.PriceCategoryLabel:
    price_category_label = models.PriceCategoryLabel.query.filter_by(label=label, venue=venue).one_or_none()
    if not price_category_label:
        return models.PriceCategoryLabel(label=label, venue=venue)
    return price_category_label


def create_price_category(offer: models.Offer, label: str, price: decimal.Decimal) -> models.PriceCategory:
    validation.check_stock_price(price, offer)
    price_category_label = get_or_create_label(label, offer.venue)
    created_price_category = models.PriceCategory(offer=offer, price=price, priceCategoryLabel=price_category_label)
    repository.add_to_session(created_price_category)
    return created_price_category


def edit_price_category(
    offer: models.Offer,
    price_category: models.PriceCategory,
    label: str | T_UNCHANGED = UNCHANGED,
    price: decimal.Decimal | T_UNCHANGED = UNCHANGED,
    editing_provider: providers_models.Provider | None = None,
) -> models.PriceCategory:
    validation.check_price_category_is_updatable(price_category, editing_provider)

    if price is not UNCHANGED and price != price_category.price:
        validation.check_stock_price(price, offer)
        price_category.price = price

    if label is not UNCHANGED and label != price_category.label:
        price_category_label = get_or_create_label(label, offer.venue)
        price_category.priceCategoryLabel = price_category_label

    repository.add_to_session(price_category)

    stocks_to_edit = [stock for stock in offer.stocks if stock.priceCategoryId == price_category.id]
    for stock in stocks_to_edit:
        edit_stock(stock, price=price_category.price, editing_provider=editing_provider)

    return price_category


def delete_price_category(offer: models.Offer, price_category: models.PriceCategory) -> None:
    """
    Deletes a price category and its related stocks, by cascade, if the offer is still in draft.
    The stock is truly deleted instead of being soft deleted.
    """
    validation.check_price_categories_deletable(offer)
    db.session.delete(price_category)
    db.session.commit()
