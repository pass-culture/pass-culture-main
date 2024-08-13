import dataclasses
import datetime
import decimal
import enum
import logging
import typing

from flask_sqlalchemy import BaseQuery
from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2.extras import DateTimeRange
import sentry_sdk
import sqlalchemy as sa
import sqlalchemy.exc as sqla_exc
from werkzeug.exceptions import BadRequest

from pcapi import settings
from pcapi.connectors.ems import EMSAPIException
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import remove_thumb
from pcapi.connectors.titelive import get_new_product_from_ean13
from pcapi.core import search
import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
from pcapi.core.bookings.models import BookingCancellationReasons
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import validation as educational_validation
from pcapi.core.educational.api import offer as educational_api_offer
import pcapi.core.educational.api.national_program as national_program_api
from pcapi.core.external import compliance
from pcapi.core.external.attributes.api import update_external_pro
import pcapi.core.external_bookings.api as external_bookings_api
from pcapi.core.external_bookings.boost.exceptions import BoostAPIException
from pcapi.core.external_bookings.cds.exceptions import CineDigitalServiceAPIException
from pcapi.core.external_bookings.cgr.exceptions import CGRAPIException
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
import pcapi.core.finance.conf as finance_conf
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.allocine import get_allocine_products_provider
from pcapi.core.providers.constants import GTL_IDS_BY_MUSIC_GENRE_CODE
from pcapi.core.providers.constants import MUSIC_SLUG_BY_GTL_ID
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
from pcapi.core.providers.repository import get_provider_by_local_class
import pcapi.core.users.models as users_models
from pcapi.domain import music_types
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.models import pc_object
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import atomic
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.utils import image_conversion
import pcapi.utils.cinema_providers as cinema_providers_utils
from pcapi.utils.custom_logic import OPERATIONS
from pcapi.utils.date import local_datetime_to_default_timezone
from pcapi.workers import push_notification_job

from . import exceptions
from . import models
from . import repository as offers_repository
from . import schemas
from . import validation


logger = logging.getLogger(__name__)

AnyOffer = educational_api_offer.AnyCollectiveOffer | models.Offer

OFFERS_RECAP_LIMIT = 501


OFFER_LIKE_MODELS = {
    "Offer",
    "CollectiveOffer",
    "CollectiveOfferTemplate",
}


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN


@dataclasses.dataclass
class StocksStats:
    oldest_stock: datetime.datetime | None
    newest_stock: datetime.datetime | None
    stock_count: int | None
    remaining_quantity: int | None


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
        offererAddressId=venue.offererAddressId,
    )


def deserialize_extra_data(initial_extra_data: typing.Any) -> typing.Any:
    extra_data: dict = initial_extra_data
    if not extra_data:
        return None
    # FIXME (ghaliela, 2024-02-16): If gtl id is sent in the extra data, musicType and musicSubType are not sent
    if extra_data.get("gtl_id"):
        extra_data["musicType"] = str(music_types.MUSIC_TYPES_BY_SLUG[MUSIC_SLUG_BY_GTL_ID[extra_data["gtl_id"]]].code)
        extra_data["musicSubType"] = str(
            music_types.MUSIC_SUB_TYPES_BY_SLUG[MUSIC_SLUG_BY_GTL_ID[extra_data["gtl_id"]]].code
        )
    # FIXME (ghaliela, 2024-02-16): If musicType is sent in the extra data, gtl id is not sent
    elif extra_data.get("musicType"):
        extra_data["gtl_id"] = GTL_IDS_BY_MUSIC_GENRE_CODE[int(extra_data["musicType"])]
    return extra_data


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


def create_draft_offer(body: schemas.PostDraftOfferBodyModel, venue: offerers_models.Venue) -> models.Offer:
    validation.check_offer_subcategory_is_valid(body.subcategory_id)

    fields = {key: value for key, value in body.dict(by_alias=True).items() if key != "venueId"}
    offer = models.Offer(
        **fields,
        venue=venue,
        audioDisabilityCompliant=venue.audioDisabilityCompliant,
        mentalDisabilityCompliant=venue.mentalDisabilityCompliant,
        motorDisabilityCompliant=venue.motorDisabilityCompliant,
        visualDisabilityCompliant=venue.visualDisabilityCompliant,
        offererAddress=venue.offererAddress,
        isActive=False,
        validation=models.OfferValidationStatus.DRAFT,
    )
    db.session.add(offer)

    update_external_pro(venue.bookingEmail)

    return offer


def _get_field(obj: typing.Any, aliases: set, updates: dict, field: str) -> typing.Any:
    if field not in aliases:
        raise ValueError(f"Unknown schema field: {field}")
    return updates.get(field, getattr(obj, field))


def update_draft_offer(offer: models.Offer, body: schemas.PatchDraftOfferBodyModel) -> models.Offer:
    fields = body.dict(by_alias=True, exclude_unset=True)
    updates = {key: value for key, value in fields.items() if getattr(offer, key) != value}
    if not updates:
        return offer

    for key, value in updates.items():
        setattr(offer, key, value)
    db.session.add(offer)

    return offer


def update_draft_offer_useful_informations(
    offer: models.Offer,
    body: schemas.PatchDraftOfferUsefulInformationsBodyModel,
    is_from_private_api: bool = False,
) -> models.Offer:
    aliases = set(body.dict(by_alias=True))
    fields = body.dict(by_alias=True, exclude_unset=True)

    _extra_data = deserialize_extra_data(fields.get("extraData", offer.extraData))
    fields["extraData"] = _format_extra_data(offer.subcategoryId, _extra_data) or {}

    should_send_mail = fields.pop("shouldSendMail", False)
    updates = {key: value for key, value in fields.items() if getattr(offer, key) != value}
    if not updates:
        return offer

    audio_disability_compliant = _get_field(offer, aliases, updates, "audioDisabilityCompliant")
    mental_disability_compliant = _get_field(offer, aliases, updates, "mentalDisabilityCompliant")
    motor_disability_compliant = _get_field(offer, aliases, updates, "motorDisabilityCompliant")
    visual_disability_compliant = _get_field(offer, aliases, updates, "visualDisabilityCompliant")
    booking_contact = _get_field(offer, aliases, updates, "bookingContact")
    extra_data = _get_field(offer, aliases, updates, "extraData")
    is_duo = _get_field(offer, aliases, updates, "isDuo")
    withdrawal_delay = _get_field(offer, aliases, updates, "withdrawalDelay")
    withdrawal_type = _get_field(offer, aliases, updates, "withdrawalType")

    validation.check_validation_status(offer)
    validation.check_accessibility_compliance(
        audio_disability_compliant, mental_disability_compliant, motor_disability_compliant, visual_disability_compliant
    )
    validation.check_offer_extra_data(
        offer.subcategoryId,
        extra_data,
        offer.venue,
        is_from_private_api,
        offer,
    )
    validation.check_is_duo_compliance(
        is_duo,
        offer.subcategory,
    )
    validation.check_offer_withdrawal(
        withdrawal_type,
        withdrawal_delay,
        offer.subcategoryId,
        booking_contact,
        offer.lastProvider,
    )
    validation.check_digital_offer_fields(offer)

    if offer.is_soft_deleted():
        raise pc_object.DeletedRecordException()

    for key, value in updates.items():
        setattr(offer, key, value)

    db.session.add(offer)

    withdrawal_fields = ("withdrawalType", "withdrawalDelay", "bookingContact", "withdrawalDetails")
    withdrawal_updated = set(updates).intersection(withdrawal_fields)
    if should_send_mail and withdrawal_updated:
        transactional_mails.send_email_for_each_ongoing_booking(offer)

    search.async_index_offer_ids(
        [offer.id],
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"changes": set(updates)},
    )

    return offer


def create_offer(
    audio_disability_compliant: bool,
    mental_disability_compliant: bool,
    motor_disability_compliant: bool,
    name: str,
    subcategory_id: str,
    venue: offerers_models.Venue,
    visual_disability_compliant: bool,
    booking_contact: str | None = None,
    booking_email: str | None = None,
    description: str | None = None,
    duration_minutes: int | None = None,
    external_ticket_office_url: str | None = None,
    extra_data: dict | None = None,
    is_duo: bool | None = None,
    is_national: bool | None = None,
    offerer_address: offerers_models.OffererAddress | None = None,
    provider: providers_models.Provider | None = None,
    url: str | None = None,
    withdrawal_delay: int | None = None,
    withdrawal_details: str | None = None,
    withdrawal_type: models.WithdrawalTypeEnum | None = None,
    is_from_private_api: bool = False,
    id_at_provider: str | None = None,
    venue_provider: providers_models.VenueProvider | None = None,
) -> models.Offer:
    validation.check_offer_withdrawal(
        withdrawal_type, withdrawal_delay, subcategory_id, booking_contact, provider, venue_provider
    )
    validation.check_offer_subcategory_is_valid(subcategory_id)
    formatted_extra_data = _format_extra_data(subcategory_id, extra_data)
    validation.check_offer_extra_data(subcategory_id, formatted_extra_data, venue, is_from_private_api)
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id]
    validation.check_is_duo_compliance(is_duo, subcategory)
    validation.check_can_input_id_at_provider(provider, id_at_provider)
    validation.check_can_input_id_at_provider_for_this_venue(venue.id, id_at_provider)

    is_national = True if url else bool(is_national)

    offer = models.Offer(
        audioDisabilityCompliant=audio_disability_compliant,
        bookingContact=booking_contact,
        bookingEmail=booking_email,
        description=description,
        durationMinutes=duration_minutes,
        externalTicketOfficeUrl=external_ticket_office_url,
        extraData=formatted_extra_data or {},
        isActive=False,
        isDuo=bool(is_duo),
        isNational=is_national,
        mentalDisabilityCompliant=mental_disability_compliant,
        motorDisabilityCompliant=motor_disability_compliant,
        lastProvider=provider,
        subcategoryId=subcategory_id,
        name=name,
        url=url,
        validation=models.OfferValidationStatus.DRAFT,
        venue=venue,
        visualDisabilityCompliant=visual_disability_compliant,
        withdrawalDelay=withdrawal_delay,
        withdrawalDetails=withdrawal_details,
        withdrawalType=withdrawal_type,
        # WARNING: quid des offres numériques ici ?
        offererAddress=offerer_address or venue.offererAddress,
        idAtProvider=id_at_provider,
    )
    repository.add_to_session(offer)
    db.session.flush()

    logger.info(
        "models.Offer has been created",
        extra={"offer_id": offer.id, "venue_id": venue.id, "product_id": offer.productId},
        technical_message_id="offer.created",
    )

    update_external_pro(venue.bookingEmail)

    return offer


def update_offer(
    offer: models.Offer,
    audioDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    bookingContact: str | None | T_UNCHANGED = UNCHANGED,
    bookingEmail: str | None | T_UNCHANGED = UNCHANGED,
    description: str | None | T_UNCHANGED = UNCHANGED,
    durationMinutes: int | None | T_UNCHANGED = UNCHANGED,
    externalTicketOfficeUrl: str | None | T_UNCHANGED = UNCHANGED,
    extraData: dict | None | T_UNCHANGED = UNCHANGED,
    isActive: bool | T_UNCHANGED = UNCHANGED,
    isDuo: bool | T_UNCHANGED = UNCHANGED,
    isNational: bool | T_UNCHANGED = UNCHANGED,
    mentalDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    motorDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    name: str | T_UNCHANGED = UNCHANGED,
    url: str | None | T_UNCHANGED = UNCHANGED,
    visualDisabilityCompliant: bool | T_UNCHANGED = UNCHANGED,
    withdrawalDelay: int | None | T_UNCHANGED = UNCHANGED,
    withdrawalDetails: str | None | T_UNCHANGED = UNCHANGED,
    withdrawalType: models.WithdrawalTypeEnum | None | T_UNCHANGED = UNCHANGED,
    shouldSendMail: bool = False,
    is_from_private_api: bool = False,
    idAtProvider: str | None | T_UNCHANGED = UNCHANGED,
    offererAddress: offerers_models.OffererAddress | None | T_UNCHANGED = UNCHANGED,
) -> models.Offer:
    modifications = {
        field: new_value
        for field, new_value in locals().items()
        if field not in ("offer", "shouldSendMail", "is_from_private_api")
        and new_value is not UNCHANGED  # has the user provided a value for this field
        and getattr(offer, field) != new_value  # is the value different from what we have on database?
    }
    if not modifications:
        return offer

    validation.check_validation_status(offer)
    if extraData is not UNCHANGED:
        formatted_extra_data = _format_extra_data(offer.subcategoryId, extraData)
        validation.check_offer_extra_data(
            offer.subcategoryId, formatted_extra_data, offer.venue, is_from_private_api, offer
        )
    if isDuo is not UNCHANGED:
        validation.check_is_duo_compliance(isDuo, offer.subcategory)

    if idAtProvider is not UNCHANGED:
        validation.check_can_input_id_at_provider(offer.lastProvider, idAtProvider)
        validation.check_can_input_id_at_provider_for_this_venue(offer.venueId, idAtProvider, offer.id)

    withdrawal_updated = not (
        withdrawalType is UNCHANGED
        and withdrawalDelay is UNCHANGED
        and withdrawalDetails is UNCHANGED
        and bookingContact is UNCHANGED
    )
    if withdrawal_updated:
        changed_withdrawalType = offer.withdrawalType if withdrawalType is UNCHANGED else withdrawalType
        changed_withdrawalDelay = offer.withdrawalDelay if withdrawalDelay is UNCHANGED else withdrawalDelay
        changed_bookingContact = offer.bookingContact if bookingContact is UNCHANGED else bookingContact

        if not (withdrawalType is UNCHANGED and withdrawalDelay is UNCHANGED and changed_bookingContact is UNCHANGED):
            validation.check_offer_withdrawal(
                changed_withdrawalType,
                changed_withdrawalDelay,
                offer.subcategoryId,
                changed_bookingContact,
                offer.lastProvider,
            )

    if offer.lastProvider is not None:
        validation.check_update_only_allowed_fields_for_offer_from_provider(set(modifications), offer.lastProvider)

    if offer.is_soft_deleted():
        raise pc_object.DeletedRecordException()

    for key, value in modifications.items():
        setattr(offer, key, value)
    if offer.isFromAllocine:
        offer.fieldsUpdated = list(set(offer.fieldsUpdated) | set(modifications))

    repository.add_to_session(offer)

    logger.info("Offer has been updated", extra={"offer_id": offer.id}, technical_message_id="offer.updated")

    if shouldSendMail and withdrawal_updated:
        transactional_mails.send_email_for_each_ongoing_booking(offer)

    search.async_index_offer_ids(
        [offer.id],
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"changes": set(modifications.keys())},
    )

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

    new_venue = None
    if "venueId" in new_values and new_values["venueId"] != offer_to_update.venueId:
        offerer = offerers_repository.get_by_collective_offer_id(offer_to_update.id)
        new_venue = offerers_api.get_venue_by_id(new_values["venueId"])
        if not new_venue:
            raise educational_exceptions.VenueIdDontExist()
        if new_venue.managingOffererId != offerer.id:
            raise educational_exceptions.OffererOfVenueDontMatchOfferer()

    nationalProgramId = new_values.pop("nationalProgramId", None)
    try:
        national_program_api.link_or_unlink_offer_to_program(nationalProgramId, offer_to_update, commit=False)
    except Exception:
        db.session.rollback()
        raise

    with atomic():
        updated_fields = _update_collective_offer(offer=offer_to_update, new_values=new_values, commit=False)
        if new_venue:
            educational_models.CollectiveBooking.query.filter(
                educational_models.CollectiveBooking.collectiveStockId == offer_to_update.collectiveStock.id
            ).update({"venueId": new_venue.id}, synchronize_session="fetch")

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

    nationalProgramId = new_values.pop("nationalProgramId", None)
    national_program_api.link_or_unlink_offer_to_program(nationalProgramId, offer_to_update)

    if "dates" in new_values:
        dates = new_values.pop("dates", None)
        if dates:
            start, end = dates["start"], dates["end"]
            if start.date() < offer_to_update.dateCreated.date():
                raise educational_exceptions.StartsBeforeOfferCreation()
            offer_to_update.dateRange = DateTimeRange(start, end)
        else:
            offer_to_update.dateRange = None

    _update_collective_offer(offer=offer_to_update, new_values=new_values)

    search.async_index_collective_offer_template_ids(
        [offer_to_update.id],
        reason=search.IndexationReason.OFFER_UPDATE,
    )


def _update_collective_offer(
    offer: educational_api_offer.AnyCollectiveOffer, new_values: dict, commit: bool = True
) -> list[str]:
    validation.check_validation_status(offer)
    validation.check_contact_request(offer, new_values)
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

    if commit:
        db.session.commit()

    return updated_fields


def batch_update_offers(query: BaseQuery, update_fields: dict, send_email_notification: bool = False) -> None:
    query = query.filter(models.Offer.validation == models.OfferValidationStatus.APPROVED)
    raw_results = query.with_entities(models.Offer.id, models.Offer.venueId).all()
    offer_ids: typing.Sequence[int] = []
    venue_ids: typing.Sequence[int] = []
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

        search.async_index_offer_ids(
            offer_ids_batch,
            reason=search.IndexationReason.OFFER_BATCH_UPDATE,
            log_extra={"changes": set(update_fields.keys())},
        )

        withdrawal_updated = {"withdrawalDetails", "withdrawalType", "withdrawalDelay"}.intersection(
            update_fields.keys()
        )
        if send_email_notification and withdrawal_updated:
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

        search.async_index_collective_offer_template_ids(
            collective_offer_template_ids_batch,
            reason=search.IndexationReason.OFFER_BATCH_UPDATE,
            log_extra={"changes": set(update_fields.keys())},
        )


def activate_future_offers(publication_date: datetime.datetime | None = None) -> None:
    query = offers_repository.get_offers_by_publication_date(publication_date=publication_date)
    query = offers_repository.exclude_offers_from_inactive_venue_provider(query)
    batch_update_offers(query, {"isActive": True})


def _notify_pro_upon_stock_edit_for_event_offer(stock: models.Stock, bookings: list[bookings_models.Booking]) -> None:
    if stock.offer.isEvent:
        transactional_mails.send_event_offer_postponement_confirmation_email_to_pro(stock, len(bookings))


def _notify_beneficiaries_upon_stock_edit(stock: models.Stock, bookings: list[bookings_models.Booking]) -> None:
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
        transactional_mails.send_batch_booking_postponement_email_to_users(bookings)


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
    id_at_provider: str | None = None,
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
        priceCategory=price_category,  # type: ignore[arg-type]
        idAtProviders=id_at_provider,
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
    # offers can be created without stock in API, so we fill the lastValidationPrice at the first stock creation
    if offer.lastValidationPrice is None and offer.validation == offer_mixin.OfferValidationStatus.APPROVED:
        offer.lastValidationPrice = price
    repository.add_to_session(created_stock, *created_activation_codes, offer)
    db.session.flush()
    search.async_index_offer_ids(
        [offer.id],
        reason=search.IndexationReason.STOCK_CREATION,
    )

    return created_stock


def edit_stock(
    stock: models.Stock,
    price: decimal.Decimal | None | T_UNCHANGED = UNCHANGED,
    quantity: int | None | T_UNCHANGED = UNCHANGED,
    beginning_datetime: datetime.datetime | None | T_UNCHANGED = UNCHANGED,
    booking_limit_datetime: datetime.datetime | None | T_UNCHANGED = UNCHANGED,
    editing_provider: providers_models.Provider | None = None,
    price_category: models.PriceCategory | None | T_UNCHANGED = UNCHANGED,
    id_at_provider: str | None | T_UNCHANGED = UNCHANGED,
) -> tuple[models.Stock | None, bool]:
    """If anything has changed, return the stock and whether the
    "beginning datetime" has changed. Otherwise, return `(None, False)`.
    """
    validation.check_stock_is_updatable(stock, editing_provider)

    old_price = stock.price
    old_quantity = stock.quantity
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
        validation.check_stock_price(price, stock.offer, old_price=stock.price)

    if price_category is not UNCHANGED and price_category is not None and price_category is not stock.priceCategory:
        modifications["priceCategory"] = price_category
        modifications["price"] = price_category.price
        validation.check_stock_price(
            price_category.price,
            stock.offer,
            old_price=stock.priceCategory.price if stock.priceCategory else stock.price,
        )

    if quantity is not UNCHANGED and quantity != stock.quantity:
        modifications["quantity"] = quantity
        validation.check_stock_quantity(quantity, stock.dnBookedQuantity)

    if booking_limit_datetime is not UNCHANGED and booking_limit_datetime != stock.bookingLimitDatetime:
        modifications["bookingLimitDatetime"] = booking_limit_datetime
        validation.check_activation_codes_expiration_datetime_on_stock_edition(
            stock.activationCodes,
            booking_limit_datetime,
        )

    if beginning_datetime not in (UNCHANGED, stock.beginningDatetime):
        modifications["beginningDatetime"] = beginning_datetime

    if id_at_provider not in (UNCHANGED, stock.idAtProviders):
        modifications["idAtProviders"] = id_at_provider

    if not modifications:
        logger.info(
            "Empty update of stock",
            extra={"offer_id": stock.offerId, "stock_id": stock.id},
        )
        return None, False  # False is for `"beginningDatetime" in modifications`

    if stock.offer.isFromAllocine:
        updated_fields = set(modifications)
        validation.check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields)
        stock.fieldsUpdated = list(set(stock.fieldsUpdated) | updated_fields)

    for model_attr, value in modifications.items():
        setattr(stock, model_attr, value)

    if "beginningDatetime" in modifications:
        finance_api.update_finance_event_pricing_date(stock)

    repository.add_to_session(stock)
    search.async_index_offer_ids(
        [stock.offerId],
        reason=search.IndexationReason.STOCK_UPDATE,
        log_extra={"changes": set(modifications.keys())},
    )

    log_extra_data: dict[str, typing.Any] = {
        "offer_id": stock.offerId,
        "stock_id": stock.id,
        "stock_dnBookedQuantity": stock.dnBookedQuantity,
    }

    if (new_price := modifications.get("price", UNCHANGED)) is not UNCHANGED:
        log_extra_data["old_price"] = old_price
        log_extra_data["stock_price"] = new_price

    if (new_quantity := modifications.get("quantity", UNCHANGED)) is not UNCHANGED:
        log_extra_data["old_quantity"] = old_quantity
        log_extra_data["stock_quantity"] = new_quantity

    logger.info("Successfully updated stock", extra=log_extra_data, technical_message_id="stock.updated")

    return stock, "beginningDatetime" in modifications


def handle_stocks_edition(edited_stocks: list[tuple[models.Stock, bool]]) -> None:
    for stock, is_beginning_datetime_updated in edited_stocks:
        if is_beginning_datetime_updated:
            bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
            _notify_pro_upon_stock_edit_for_event_offer(stock, bookings)
            _notify_beneficiaries_upon_stock_edit(stock, bookings)


def _format_publication_date(publication_date: datetime.datetime | None, timezone: str) -> datetime.datetime | None:
    if publication_date is None:
        return None

    minute = publication_date.minute
    publication_date = local_datetime_to_default_timezone(publication_date, timezone)
    # Some UTC offsets may change minute (like Pacific/Marquesas UTC-09:30),
    # in this case publication_date is rounded to the next hour
    if publication_date.minute != minute:
        publication_date += datetime.timedelta(hours=1)
        publication_date = publication_date.replace(minute=0)

    publication_date = publication_date.replace(second=0, microsecond=0, tzinfo=None)
    return publication_date


def publish_offer(
    offer: models.Offer,
    user: users_models.User | None,
    publication_date: datetime.datetime | None = None,
) -> models.Offer:
    publication_date = _format_publication_date(publication_date, offer.venue.timezone)  # type: ignore[arg-type]
    validation.check_publication_date(offer, publication_date)

    update_offer_fraud_information(offer, user)

    if publication_date is not None:
        offer.isActive = False
        future_offer = models.FutureOffer(offerId=offer.id, publicationDate=publication_date)
        db.session.add(future_offer)
    else:
        if offer.publicationDate:
            offers_repository.delete_future_offer(offer.id)
        search.async_index_offer_ids(
            [offer.id],
            reason=search.IndexationReason.OFFER_PUBLICATION,
        )
        logger.info(
            "Offer has been published",
            extra={"offer_id": offer.id, "venue_id": offer.venueId, "offer_status": offer.status},
            technical_message_id="offer.published",
        )
    return offer


def update_offer_fraud_information(offer: AnyOffer, user: users_models.User | None) -> None:
    venue_already_has_validated_offer = offers_repository.venue_already_has_validated_offer(offer)

    offer.validation = set_offer_status_based_on_fraud_criteria(offer)

    if user is not None:
        offer.author = user
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None

    if offer.validation in (models.OfferValidationStatus.PENDING, models.OfferValidationStatus.REJECTED):
        offer.isActive = False
    else:
        offer.isActive = True
        if (
            isinstance(offer, models.Offer) and offer.isThing and offer.activeStocks
        ):  # public API may create offers without stocks
            offer.lastValidationPrice = offer.max_price

    if (
        offer.validation == models.OfferValidationStatus.APPROVED
        and not venue_already_has_validated_offer
        and isinstance(offer, models.Offer)
    ):
        transactional_mails.send_first_venue_approved_offer_email_to_pro(offer)


def _invalidate_bookings(bookings: list[bookings_models.Booking]) -> list[bookings_models.Booking]:
    for booking in bookings:
        if booking.status is bookings_models.BookingStatus.USED:
            bookings_api.mark_as_unused(booking)
    return bookings


def _delete_stock(stock: models.Stock) -> None:
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
            transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email(booking)
        transactional_mails.send_booking_cancellation_confirmation_by_pro_email(cancelled_bookings)

        push_notification_job.send_cancel_booking_notification.delay([booking.id for booking in cancelled_bookings])
    search.async_index_offer_ids(
        [stock.offerId],
        reason=search.IndexationReason.STOCK_DELETION,
    )


def delete_stock(stock: models.Stock) -> None:
    validation.check_stock_is_deletable(stock)
    _delete_stock(stock)


def create_mediation(
    user: users_models.User | None,
    offer: models.Offer,
    credit: str | None,
    image_as_bytes: bytes,
    crop_params: image_conversion.CropParams | None = None,
    keep_ratio: bool = False,
    min_width: int | None = validation.MIN_THUMBNAIL_WIDTH,
    min_height: int | None = validation.MIN_THUMBNAIL_HEIGHT,
    max_width: int | None = None,
    max_height: int | None = None,
    aspect_ratio: image_conversion.ImageRatio = image_conversion.ImageRatio.PORTRAIT,
) -> models.Mediation:
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

    search.async_index_offer_ids(
        [offer.id],
        reason=search.IndexationReason.MEDIATION_CREATION,
    )

    return mediation


def delete_mediation(offer: models.Offer) -> None:
    mediations = models.Mediation.query.filter(models.Mediation.offerId == offer.id).all()

    _delete_mediations_and_thumbs(mediations)

    search.async_index_offer_ids(
        [offer.id],
        reason=search.IndexationReason.MEDIATION_DELETION,
    )


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
    offer_ids = {offer_id for offer_id, in offer_ids_query.all()}

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

    search.async_index_offer_ids(
        offer_ids,
        reason=search.IndexationReason.CRITERIA_LINK,
        log_extra={"criterion_ids": criterion_ids},
    )

    return True


def reject_inappropriate_products(
    eans: list[str],
    author: users_models.User | None,
    rejected_by_fraud_action: bool = False,
    send_booking_cancellation_emails: bool = True,
) -> bool:
    products = models.Product.query.filter(
        models.Product.extraData["ean"].astext.in_(eans),
        models.Product.idAtProviders.is_not(None),
        models.Product.gcuCompatibilityType != models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
    )

    if not products:
        return False
    product_ids = [product.id for product in products]
    offers_query = models.Offer.query.filter(
        sa.or_(
            models.Offer.productId.in_(product_ids),
            models.Offer.extraData["ean"].astext.in_(eans),
        ),
        models.Offer.validation != models.OfferValidationStatus.REJECTED,
    )

    offers = offers_query.options(sa.orm.joinedload(models.Offer.stocks).joinedload(models.Stock.bookings)).all()

    offer_updated_counts = offers_query.update(
        values={
            "validation": models.OfferValidationStatus.REJECTED,
            "lastValidationDate": datetime.datetime.utcnow(),
            "lastValidationType": OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
            "lastValidationAuthorUserId": author.id if author else None,
        },
        synchronize_session=False,
    )

    for product in products:
        product.gcuCompatibilityType = (
            models.GcuCompatibilityType.FRAUD_INCOMPATIBLE
            if rejected_by_fraud_action
            else models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        )

    try:
        db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark product and offers as inappropriate: %s",
            extra={
                "eans": eans,
                "products_lenght": len(product_ids),
                "partial_products": product_ids[:30],
                "exc": str(exception),
            },
        )
        return False

    offer_ids = []
    for offer in offers:
        offer_ids.append(offer.id)
        bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)

        if send_booking_cancellation_emails:
            for booking in bookings:
                transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(
                    booking,
                    reason=BookingCancellationReasons.FRAUD,
                    rejected_by_fraud_action=rejected_by_fraud_action,
                )

    logger.info(
        "Rejected inappropriate products",
        extra={
            "eans": eans,
            "products_lenght": len(product_ids),
            "partial_products": product_ids[:30],
            "offers": offer_ids,
            "offer_updated_counts": offer_updated_counts,
        },
    )

    if offer_ids:
        users_models.Favorite.query.filter(users_models.Favorite.offerId.in_(offer_ids)).delete(
            synchronize_session=False
        )
        search.async_index_offer_ids(
            offer_ids,
            reason=search.IndexationReason.PRODUCT_REJECTION,
            log_extra={"eans": eans},
        )

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
        extra={"ean": ean, "products": [p.id for p in products], "offers": offer_ids},
    )

    search.async_index_offer_ids(
        offer_ids,
        reason=search.IndexationReason.PRODUCT_DEACTIVATION,
        log_extra={"ean": ean},
    )

    return True


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
    sub_rule_flags_offer = []
    for sub_rule in rule.subRules:
        try:
            sub_rule_flags_offer.append(resolve_offer_validation_sub_rule(sub_rule, offer))
        except exceptions.UnapplicableModel:
            sub_rule_flags_offer.append(False)
            break
    is_offer_flagged = all(sub_rule_flags_offer)
    return is_offer_flagged


def set_offer_status_based_on_fraud_criteria(offer: AnyOffer) -> models.OfferValidationStatus:
    status = models.OfferValidationStatus.APPROVED

    confidence_level = offerers_api.get_offer_confidence_level(offer.venue)

    if confidence_level == offerers_models.OffererConfidenceLevel.WHITELIST:
        logger.info("Computed offer validation", extra={"offer": offer.id, "status": status.value, "whitelist": True})
        return status

    if confidence_level == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW:
        status = models.OfferValidationStatus.PENDING
        # continue so that offers are checked against rules: gives more information for manual validation

    offer_validation_rules = (
        models.OfferValidationRule.query.options(
            sa.orm.joinedload(models.OfferValidationSubRule, models.OfferValidationRule.subRules)
        )
        .filter(models.OfferValidationRule.isActive.is_(True))
        .all()
    )

    flagging_rules = []
    for rule in offer_validation_rules:
        if rule_flags_offer(rule, offer):
            flagging_rules.append(rule)

    if flagging_rules:
        status = models.OfferValidationStatus.PENDING
        offer.flaggingValidationRules = flagging_rules
        if isinstance(offer, models.Offer):
            compliance.update_offer_compliance_score(offer, is_primary=True)
    else:
        if isinstance(offer, models.Offer):
            compliance.update_offer_compliance_score(offer, is_primary=False)

    logger.info("Computed offer validation", extra={"offer": offer.id, "status": status.value})
    return status


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

    transactional_mails.send_email_reported_offer_by_user(user, offer, reason, custom_reason)


def get_shows_remaining_places_from_provider(provider_class: str | None, offer: models.Offer) -> dict[str, int]:
    match provider_class:
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
                return {}
            return external_bookings_api.get_shows_stock(offer.venueId, cleaned_show_ids)
        case "BoostStocks":
            if not FeatureToggle.ENABLE_BOOST_API_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_BOOST_API_INTEGRATION is inactive")
            film_id = cinema_providers_utils.get_boost_or_cgr_or_ems_film_id_from_uuid(offer.idAtProvider)
            if not film_id:
                return {}
            return external_bookings_api.get_movie_stocks(offer.venueId, film_id)
        case "CGRStocks":
            if not FeatureToggle.ENABLE_CGR_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CGR_INTEGRATION is inactive")
            cgr_allocine_film_id = cinema_providers_utils.get_boost_or_cgr_or_ems_film_id_from_uuid(offer.idAtProvider)
            if not cgr_allocine_film_id:
                return {}
            return external_bookings_api.get_movie_stocks(offer.venueId, cgr_allocine_film_id)
        case "EMSStocks":
            if not FeatureToggle.ENABLE_EMS_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_EMS_INTEGRATION is inactive")
            film_id = cinema_providers_utils.get_boost_or_cgr_or_ems_film_id_from_uuid(offer.idAtProvider)
            if not film_id:
                return {}
            return external_bookings_api.get_movie_stocks(offer.venueId, film_id)
    raise ValueError(f"Unknown Provider: {provider_class}")


def update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer: models.Offer) -> models.Offer:
    try:
        venue_provider = external_bookings_api.get_active_cinema_venue_provider(offer.venueId)
        validation.check_offer_is_from_current_cinema_provider(offer)
    except (exceptions.UnexpectedCinemaProvider, providers_exceptions.InactiveProvider):
        offer.isActive = False
        db.session.add(offer)
        db.session.flush()
        search.async_index_offer_ids(
            [offer.id],
            reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
            log_extra={"active": False},
        )
        return

    sentry_sdk.set_tag("cinema-venue-provider", venue_provider.provider.localClass)
    logger.info(
        "Getting up-to-date show stock from booking provider on offer view",
        extra={"offer": offer.id, "venue_provider": venue_provider.id},
    )
    offer_current_stocks = offer.bookableStocks

    try:
        shows_remaining_places = get_shows_remaining_places_from_provider(venue_provider.provider.localClass, offer)
    except (EMSAPIException, BoostAPIException, CineDigitalServiceAPIException, CGRAPIException) as e:
        # If we can't retrieve the stocks from the provider, we stop here to avoid breaking the code following this function
        # This is not ideal, I believe this function should be called on its own, or asynchronously
        # However this means frontend code (probably) so this temporarily fixes crashes for end users
        # TODO: (lixxday, 29/05/2024): remove this try/catch when th function is no longer called directly in GET /offer route
        logger.exception(
            "Failed to get shows remaining places from provider",
            extra={"offer": offer.id, "provider": venue_provider.provider.localClass, "error": e},
        )
        return
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(
            "Unknown error when getting shows remaining places from provider",
            extra={"offer": offer.id, "provider": venue_provider.provider.localClass, "error": e},
        )
        return

    offer_has_new_sold_out_stock = False
    for stock in offer_current_stocks:
        showtime_id = cinema_providers_utils.get_showtime_id_from_uuid(
            stock.idAtProviders, venue_provider.provider.localClass
        )
        assert showtime_id
        remaining_places = shows_remaining_places.pop(str(showtime_id), None)
        # make this stock sold out, instead of soft-deleting it (don't update its bookings)
        logger.info(
            "Updating stock quantity to match cinema remaining places",
            extra={
                "stock_id": stock.id,
                "stock_quantity": stock.quantity,
                "stock_dnBookedQuantity": stock.dnBookedQuantity,
                "remaining_places": remaining_places,
            },
        )
        if remaining_places is None or remaining_places <= 0:
            try:
                offers_repository.update_stock_quantity_to_dn_booked_quantity(stock.id)
            except sqla_exc.InternalError:
                # The SQLAlchemy session is invalidated as soon as an InternalError is raised
                db.session.rollback()
                logger.info(
                    "Recompute dnBookedQuantity of a stock",
                    extra={"stock_id": stock.id, "stock_dnBookedQuantity": stock.dnBookedQuantity},
                )
                bookings_api.recompute_dnBookedQuantity([stock.id])
                logger.info(
                    "New value for dnBookedQuantity of a stock",
                    extra={"stock_id": stock.id, "stock_dnBookedQuantity": stock.dnBookedQuantity},
                )
                offers_repository.update_stock_quantity_to_dn_booked_quantity(stock.id)
            offer_has_new_sold_out_stock = True
        # to prevent a duo booking to fail
        if remaining_places == 1:
            stock.quantity = stock.dnBookedQuantity + 1
            db.session.add(stock)
            db.session.flush()

        logger.info(
            "Successfully updated stock quantity",
            extra={
                "stock_id": stock.id,
                "stock_quantity": stock.quantity,
                "stock_dnBookedQuantity": stock.dnBookedQuantity,
            },
        )

    if offer_has_new_sold_out_stock:
        search.async_index_offer_ids(
            [offer.id],
            reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
            log_extra={"sold_out": True},
        )

    return


def whitelist_product(idAtProviders: str) -> models.Product | None:
    titelive_product = get_new_product_from_ean13(idAtProviders)

    product = fetch_or_update_product_with_titelive_data(titelive_product)

    product.gcuCompatibilityType = models.GcuCompatibilityType.COMPATIBLE

    db.session.add(product)
    db.session.commit()
    return product


def fetch_or_update_product_with_titelive_data(titelive_product: models.Product) -> models.Product:
    product = models.Product.query.filter_by(idAtProviders=titelive_product.idAtProviders).one_or_none()
    if not product:
        return titelive_product

    product.name = titelive_product.name
    product.description = titelive_product.description
    product.subcategoryId = titelive_product.subcategoryId
    product.thumbCount = titelive_product.thumbCount
    old_extra_data = product.extraData
    if old_extra_data is None:
        old_extra_data = {}

    if titelive_product.extraData:
        product.extraData = {**old_extra_data, **titelive_product.extraData}

    return product


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


def batch_delete_stocks(stocks_to_delete: list[models.Stock]) -> None:
    # We want to check that all stocks can be deleted first
    for stock in stocks_to_delete:
        validation.check_stock_is_deletable(stock)

    for stock in stocks_to_delete:
        _delete_stock(stock)


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
        validation.check_stock_price(price, offer, old_price=price_category.price)
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


def approves_provider_product_and_rejected_offers(ean: str) -> None:
    product = models.Product.query.filter(
        models.Product.gcuCompatibilityType == models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        models.Product.extraData["ean"].astext == ean,
        models.Product.idAtProviders.is_not(None),
    ).one_or_none()

    if not product:
        raise exceptions.ProductNotFound()

    offer_ids = []
    try:
        with transaction():
            product.gcuCompatibilityType = models.GcuCompatibilityType.COMPATIBLE
            db.session.add(product)

            offers_query = models.Offer.query.filter(
                models.Offer.productId == product.id,
                models.Offer.validation == models.OfferValidationStatus.REJECTED,
                models.Offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
            ).options(sa.orm.load_only(models.Offer.id))

            offers = offers_query.all()

            offer_updated_counts = offers_query.update(
                values={
                    "validation": models.OfferValidationStatus.APPROVED,
                    "lastValidationDate": datetime.datetime.utcnow(),
                    "lastValidationType": OfferValidationType.AUTO,
                },
                synchronize_session=False,
            )

            offer_ids = [offer.id for offer in offers]

            logger.info(
                "Approve product and rejected offers",
                extra={
                    "ean": ean,
                    "product": product.id,
                    "offers": offer_ids,
                    "offer_updated_counts": offer_updated_counts,
                },
            )

        if offer_ids:
            search.async_index_offer_ids(
                set(offer_ids),
                reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
            )

    except Exception as exception:
        logger.exception(
            "Could not approve product and rejected offers: %s",
            extra={"ean": ean, "product": product.id, "offers": offer_ids, "exc": str(exception)},
        )
        raise exceptions.NotUpdateProductOrOffers(exception)


def get_stocks_stats(offer_id: int) -> StocksStats:
    data = (
        models.Stock.query.with_entities(
            sa.func.min(models.Stock.beginningDatetime),
            sa.func.max(models.Stock.beginningDatetime),
            sa.func.count(models.Stock.id),
            sa.case(
                (
                    models.Stock.query.filter(
                        models.Stock.quantity == None,
                        models.Stock.isSoftDeleted.is_(False),
                        models.Stock.offerId == offer_id,
                    ).exists(),
                    None,
                ),
                else_=sa.cast(sa.func.sum(models.Stock.quantity - models.Stock.dnBookedQuantity), sa.Integer),
            ),
        )
        .filter(models.Stock.offerId == offer_id, models.Stock.isSoftDeleted.is_(False))
        .group_by(models.Stock.offerId)
        .one_or_none()
    )
    try:
        return StocksStats(*data)
    except TypeError:
        raise ApiErrors(
            errors={
                "global": ["L'offre en cours de création ne possède aucun Stock"],
            },
            status_code=404,
        )


def fill_offer_extra_data_from_product_data(product_id: int) -> None:
    offer_ids = []

    product = models.Product.query.filter_by(id=product_id).one_or_none()

    if not product:
        raise exceptions.ProductNotFound()

    try:
        with transaction():
            offers = models.Offer.query.filter_by(productId=product_id).all()

            offer_ids = [offer.id for offer in offers]

            for offer in offers:
                offer.name = product.name
                offer.extraData = offer.extraData or {}
                offer.extraData.update(product.extraData)
                db.session.add(offer)
                logger.info(
                    "Update offer extra data from product extra data",
                    extra={"product_id": product_id, "offer_id": offer.id},
                )

        if offer_ids:
            search.async_index_offer_ids(
                set(offer_ids),
                reason=search.IndexationReason.PRODUCT_UPDATE,
                log_extra={"product_id": product_id, "updated_extra_data": True},
            )

    except Exception as exception:
        logger.exception(
            "Could not update offers extra data from product",
            extra={"product": product_id, "offers": offer_ids, "exc": str(exception)},
        )
        raise exceptions.NotUpdateProductOrOffers(exception)


def update_offers_description_from_product_description(product_id: int) -> None:
    offer_ids = []

    product = models.Product.query.filter_by(id=product_id).one_or_none()

    if not product:
        raise exceptions.ProductNotFound()

    try:
        with transaction():
            offers = models.Offer.query.filter_by(productId=product_id).all()

            offer_ids = [offer.id for offer in offers]

            for offer in offers:
                offer.description = product.description
                db.session.add(offer)
                logger.info(
                    "Update offer description from product description",
                    extra={"product_id": product_id, "offer_id": offer.id},
                )

        if offer_ids:
            search.async_index_offer_ids(
                set(offer_ids),
                reason=search.IndexationReason.PRODUCT_UPDATE,
                log_extra={"product_id": product_id, "updated_description": True},
            )

    except Exception as exception:
        logger.exception(
            "Could not update offers description from product description",
            extra={"product": product_id, "offers": offer_ids, "exc": str(exception)},
        )
        raise exceptions.NotUpdateProductOrOffers(exception)


def check_can_move_event_offer(offer: models.Offer) -> list[offerers_models.Venue]:
    if not offer.isEvent:
        raise exceptions.OfferIsNotEvent()

    count_past_stocks = (
        models.Stock.query.with_entities(models.Stock.id)
        .filter(
            models.Stock.offerId == offer.id,
            models.Stock.beginningDatetime < datetime.datetime.utcnow(),
            models.Stock.isSoftDeleted.is_(False),
        )
        .count()
    )
    if count_past_stocks > 0:
        raise exceptions.OfferEventInThePast(count_past_stocks)

    count_reimbursed_bookings = (
        bookings_models.Booking.query.with_entities(bookings_models.Booking.id)
        .join(bookings_models.Booking.stock)
        .filter(models.Stock.offerId == offer.id, bookings_models.Booking.isReimbursed)
        .count()
    )
    if count_reimbursed_bookings > 0:
        raise exceptions.OfferHasReimbursedBookings(count_reimbursed_bookings)

    venues_choices = (
        offerers_models.Venue.query.filter(
            offerers_models.Venue.managingOffererId == offer.venue.managingOffererId,
            offerers_models.Venue.id != offer.venueId,
        )
        .join(
            offerers_models.VenuePricingPointLink,
            sa.and_(
                offerers_models.VenuePricingPointLink.venueId == offerers_models.Venue.id,
                offerers_models.VenuePricingPointLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .options(
            sa.orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
            ),
            sa.orm.contains_eager(offerers_models.Venue.pricing_point_links).load_only(
                offerers_models.VenuePricingPointLink.pricingPointId, offerers_models.VenuePricingPointLink.timespan
            ),
        )
        .order_by(offerers_models.Venue.common_name)
        .all()
    )
    if not venues_choices:
        raise exceptions.NoDestinationVenue()

    return venues_choices


def _get_or_create_same_price_category_label(
    venue: offerers_models.Venue, source_price_category_label: offers_models.PriceCategoryLabel
) -> offers_models.PriceCategoryLabel:
    try:
        # Use label which already exists when found, otherwise unique_label_venue constraint would cause exception
        return next(filter(lambda pcl: pcl.label == source_price_category_label.label, venue.priceCategoriesLabel))
    except StopIteration:
        # Copy price category label from source to destination venue
        new_price_category_label = offers_models.PriceCategoryLabel(
            venue=venue, label=source_price_category_label.label
        )
        db.session.add(new_price_category_label)
        return new_price_category_label


def move_event_offer(
    offer: models.Offer, destination_venue: offerers_models.Venue, notify_beneficiary: bool = False
) -> None:
    offer_id = offer.id

    venue_choices = check_can_move_event_offer(offer)

    if destination_venue not in venue_choices:
        raise exceptions.ForbiddenDestinationVenue()

    destination_pricing_point_link = destination_venue.current_pricing_point_link
    assert destination_pricing_point_link  # for mypy - it would not be in venue_choices without link
    destination_pricing_point_id = destination_pricing_point_link.pricingPointId

    bookings = (
        bookings_models.Booking.query.join(bookings_models.Booking.stock)
        .outerjoin(
            # max 1 row joined thanks to idx_uniq_individual_booking_id
            finance_models.FinanceEvent,
            sa.and_(
                finance_models.FinanceEvent.bookingId == bookings_models.Booking.id,
                finance_models.FinanceEvent.status.in_(
                    (finance_models.FinanceEventStatus.PENDING, finance_models.FinanceEventStatus.READY)
                ),
            ),
        )
        .outerjoin(
            # max 1 row joined thanks to idx_uniq_booking_id
            finance_models.Pricing,
            sa.and_(
                finance_models.Pricing.bookingId == bookings_models.Booking.id,
                finance_models.Pricing.status != finance_models.PricingStatus.CANCELLED,
            ),
        )
        .options(
            sa.orm.load_only(bookings_models.Booking.status),
            sa.orm.contains_eager(bookings_models.Booking.finance_events).load_only(finance_models.FinanceEvent.status),
            sa.orm.contains_eager(bookings_models.Booking.pricings).load_only(
                finance_models.Pricing.pricingPointId, finance_models.Pricing.status
            ),
        )
        .filter(models.Stock.offerId == offer.id)
        .all()
    )

    # After offer is moved, price categories must remain linked to labels defined for the related venue.
    # Extra SQL queries to avoid multiplying the number of rows in case of many labels
    original_price_category_labels = {price_category.priceCategoryLabel for price_category in offer.priceCategories}
    labels_mapping = {
        price_category_label: _get_or_create_same_price_category_label(destination_venue, price_category_label)
        for price_category_label in original_price_category_labels
    }
    with transaction():
        offer.venue = destination_venue
        offer.offererAddressId = destination_venue.offererAddressId
        db.session.add(offer)

        for price_category in offer.priceCategories:
            price_category.priceCategoryLabel = labels_mapping[price_category.priceCategoryLabel]
            db.session.add(price_category)

        for booking in bookings:
            assert not booking.isReimbursed
            booking.venueId = destination_venue.id

            # when offer has priced bookings, pricing point for destination venue must be the same as pricing point
            # used for pricing (same as venue pricing point at the time pricing was processed)
            pricing = booking.pricings[0] if booking.pricings else None
            if pricing and pricing.pricingPointId != destination_pricing_point_id:
                raise exceptions.BookingsHaveOtherPricingPoint()

            finance_event = booking.finance_events[0] if booking.finance_events else None
            if finance_event:
                finance_event.venueId = destination_venue.id
                finance_event.pricingPointId = destination_pricing_point_id
                if finance_event.status == finance_models.FinanceEventStatus.PENDING:
                    finance_event.status = finance_models.FinanceEventStatus.READY
                    finance_event.pricingOrderingDate = finance_api.get_pricing_ordering_date(booking)
                db.session.add(finance_event)

            db.session.add(booking)

    search.async_index_offer_ids(
        {offer_id}, reason=search.IndexationReason.OFFER_UPDATE, log_extra={"changes": {"venueId"}}
    )

    if notify_beneficiary:
        transactional_mails.send_email_for_each_ongoing_booking(offer)


def update_used_stock_price(stock: models.Stock, new_price: float) -> None:
    if not stock.offer.isEvent:
        raise ValueError("Only stocks associated with an event offer can be edited with used bookings")

    stock.price = new_price
    bookings_models.Booking.query.filter(
        bookings_models.Booking.stockId == stock.id,
    ).update({bookings_models.Booking.amount: new_price})

    first_finance_event = (
        finance_models.FinanceEvent.query.join(bookings_models.Booking, finance_models.FinanceEvent.booking)
        .filter(
            finance_models.FinanceEvent.status != finance_models.FinanceEventStatus.CANCELLED,
            bookings_models.Booking.stockId == stock.id,
        )
        .order_by(
            finance_models.FinanceEvent.pricingOrderingDate,
            finance_models.FinanceEvent.id,
        )
        .options(
            sa.orm.joinedload(finance_models.FinanceEvent.booking),
        )
        .first()
    )

    if first_finance_event:
        finance_api.force_event_repricing(
            event=first_finance_event,
            reason=finance_models.PricingLogReason.CHANGE_AMOUNT,
        )


def upsert_movie_product_from_provider(
    movie: offers_models.Movie, provider: providers_models.Provider, id_at_providers: str
) -> offers_models.Product | None:
    if not movie.allocine_id and not movie.visa:
        logger.warning("Cannot create a movie product without allocineId nor visa")
        return None

    existing_product = None
    if movie.allocine_id:
        existing_product = offers_repository.get_movie_product_by_allocine_id(movie.allocine_id)
    if not existing_product and movie.visa:
        existing_product = offers_repository.get_movie_product_by_visa(movie.visa)

    with transaction():
        if existing_product:
            if _is_allocine(provider.id) or provider.id == existing_product.lastProviderId:
                _update_movie_product(existing_product, movie, provider.id, id_at_providers)
            return existing_product

        product = offers_models.Product(
            description=movie.description,
            durationMinutes=movie.duration,
            extraData=None,
            idAtProviders=id_at_providers,
            lastProviderId=provider.id,
            name=movie.title,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        _update_product_extra_data(product, movie)
        db.session.add(product)
    return product


def _is_allocine(provider_id: int) -> bool:
    allocine_products_provider_id = get_allocine_products_provider().id
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    return provider_id in (allocine_products_provider_id, allocine_stocks_provider_id)


def _update_movie_product(
    product: offers_models.Product, movie: offers_models.Movie, provider_id: int, id_at_providers: str
) -> None:
    product.description = movie.description
    product.durationMinutes = movie.duration
    product.idAtProviders = id_at_providers
    product.lastProviderId = provider_id
    product.name = movie.title
    _update_product_extra_data(product, movie)


def _update_product_extra_data(product: offers_models.Product, movie: offers_models.Movie) -> None:
    product.extraData = product.extraData or offers_models.OfferExtraData()
    extra_data = movie.extra_data or offers_models.OfferExtraData()
    if movie.allocine_id:
        extra_data["allocineId"] = int(movie.allocine_id)
    if movie.visa:
        extra_data["visa"] = movie.visa

    product.extraData.update((key, value) for key, value in extra_data.items() if value is not None)  # type: ignore[typeddict-item]
