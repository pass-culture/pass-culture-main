import dataclasses
import datetime
import decimal
from pcapi.core.offers import utils as offers_utils
from pcapi.core.offerers.models import ApiKey
import enum
import functools
import logging
import time
import typing
from contextlib import suppress
from functools import partial

import sentry_sdk
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from werkzeug.exceptions import BadRequest

import pcapi.core.bookings.api as bookings_api
from pcapi.models import api_errors
import pcapi.core.bookings.exceptions as bookings_exceptions
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.criteria.models as criteria_models
import pcapi.core.external_bookings.api as external_bookings_api
import pcapi.core.finance.conf as finance_conf
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.validation as offers_validation
import pcapi.core.offers.constants as offers_constants
import pcapi.core.offers.exceptions as offers_exceptions
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
import pcapi.utils.cinema_providers as cinema_providers_utils
from pcapi import settings
from pcapi.connectors.ems import EMSAPIException
from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import remove_thumb
from pcapi.connectors.titelive import get_new_product_from_ean13
from pcapi.core import search
from pcapi.routes.public.individual_offers.v1 import serialization as individual_offers_v1_serialization
from pcapi.routes.public.individual_offers.v1 import utils as individual_offers_v1_utils
from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.external import compliance
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.external_bookings.boost.exceptions import BoostAPIException
from pcapi.core.external_bookings.cds.exceptions import CineDigitalServiceAPIException
from pcapi.core.external_bookings.cgr.exceptions import CGRAPIException
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import utils as finance_utils
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.allocine import get_allocine_products_provider
from pcapi.core.providers.constants import GTL_IDS_BY_MUSIC_GENRE_CODE
from pcapi.core.providers.constants import MUSIC_SLUG_BY_GTL_ID
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.reminders.external import reminders_notifications
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.models import pc_object
from pcapi.models.api_errors import ApiErrors
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.models.pc_object import BaseQuery
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import is_managed_transaction
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.repository.session_management import on_commit
from pcapi.utils import db as db_utils
from pcapi.utils import image_conversion
from pcapi.utils.chunks import get_chunks
from pcapi.utils.custom_keys import get_field
from pcapi.utils.custom_logic import OPERATIONS
from pcapi.utils.date import local_datetime_to_default_timezone
from pcapi.workers import push_notification_job

from . import exceptions
from . import models
from . import repository as offers_repository
from . import schemas as offers_schemas
from . import validation


logger = logging.getLogger(__name__)

AnyOffer = educational_api_offer.AnyCollectiveOffer | models.Offer

OFFERS_RECAP_LIMIT = 101


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
    *,
    id_at_provider: str | None,
    provider_id: int | None,
    offerer_address_id: int | None = None,
) -> models.Offer:
    return models.Offer(
        bookingEmail=venue.bookingEmail,
        ean=product.ean,
        idAtProvider=id_at_provider,
        lastProviderId=provider_id,
        name=product.name,
        productId=product.id,
        venueId=venue.id,
        subcategoryId=product.subcategoryId,
        withdrawalDetails=venue.withdrawalDetails,
        offererAddressId=venue.offererAddressId if offerer_address_id is None else offerer_address_id,
    )


def deserialize_extra_data(initial_extra_data: typing.Any, subcategoryId: str) -> typing.Any:
    extra_data: dict = initial_extra_data
    if not extra_data:
        return None

    if subcategoryId in subcategories.MUSIC_SUBCATEGORIES:
        # FIXME (ghaliela, 2024-02-16): If gtl id is sent in the extra data, musicType and musicSubType are not sent
        gtl_id = extra_data.get("gtl_id")
        if gtl_id and gtl_id in TITELIVE_MUSIC_GENRES_BY_GTL_ID:
            extra_data["musicType"] = str(music.MUSIC_TYPES_BY_SLUG[MUSIC_SLUG_BY_GTL_ID[gtl_id]].code)
            extra_data["musicSubType"] = str(music.MUSIC_SUB_TYPES_BY_SLUG[MUSIC_SLUG_BY_GTL_ID[gtl_id]].code)
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


def _get_accessibility_compliance_fields(venue: offerers_models.Venue) -> dict:
    if venue.external_accessibility_id:
        return _get_external_accessibility_compliance(venue)
    return _get_internal_accessibility_compliance(venue)


def _get_external_accessibility_compliance(venue: offerers_models.Venue) -> dict:
    assert venue.accessibilityProvider  # helps mypy, already checked in caller
    accessibility_data = acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(
        venue.accessibilityProvider.externalAccessibilityData
    )
    return {
        "audioDisabilityCompliant": accessibility_data.isAccessibleAudioDisability,
        "mentalDisabilityCompliant": accessibility_data.isAccessibleMentalDisability,
        "motorDisabilityCompliant": accessibility_data.isAccessibleMotorDisability,
        "visualDisabilityCompliant": accessibility_data.isAccessibleVisualDisability,
    }


def _get_internal_accessibility_compliance(venue: offerers_models.Venue) -> dict:
    return {
        "audioDisabilityCompliant": venue.audioDisabilityCompliant,
        "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
        "motorDisabilityCompliant": venue.motorDisabilityCompliant,
        "visualDisabilityCompliant": venue.visualDisabilityCompliant,
    }


def create_draft_offer(
    body: offers_schemas.PostDraftOfferBodyModel,
    venue: offerers_models.Venue,
    product: offers_models.Product | None = None,
    is_from_private_api: bool = True,
) -> models.Offer:
    validation.check_offer_subcategory_is_valid(body.subcategory_id)
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[body.subcategory_id]
    validation.check_url_is_coherent_with_subcategory(subcategory, body.url)
    validation.check_offer_name_does_not_contain_ean(body.name)

    body.extra_data = _format_extra_data(body.subcategory_id, body.extra_data) or {}
    body_ean = body.extra_data.pop("ean", None)
    validation.check_offer_extra_data(body.subcategory_id, body.extra_data, venue, is_from_private_api, ean=body_ean)

    validation.check_product_for_venue_and_subcategory(product, body.subcategory_id, venue.venueTypeCode)

    fields = {key: value for key, value in body.dict(by_alias=True).items() if key not in ("venueId", "callId")}
    fields.update({"ean": body_ean})
    fields.update(_get_accessibility_compliance_fields(venue))
    fields.update({"withdrawalDetails": venue.withdrawalDetails})
    fields.update({"isDuo": bool(subcategory and subcategory.is_event and subcategory.can_be_duo)})
    if product:
        fields.pop("extraData", None)

    offer = models.Offer(
        **fields,
        venue=venue,
        isActive=False,
        validation=models.OfferValidationStatus.DRAFT,
        product=product,
    )
    db.session.add(offer)
    db.session.flush()

    update_external_pro(venue.bookingEmail)

    return offer


def update_draft_offer(offer: models.Offer, body: offers_schemas.PatchDraftOfferBodyModel) -> models.Offer:
    fields = body.dict(by_alias=True, exclude_unset=True)
    body_ean = body.extra_data.get("ean", None) if body.extra_data else None
    if body_ean:
        fields["ean"] = fields["extraData"].pop("ean")

    updates = {key: value for key, value in fields.items() if getattr(offer, key) != value}
    if not updates:
        return offer

    if body.name:
        validation.check_offer_name_does_not_contain_ean(body.name)

    if "extraData" in updates or "ean" in updates:
        formatted_extra_data = _format_extra_data(offer.subcategoryId, body.extra_data) or {}
        validation.check_offer_extra_data(
            offer.subcategoryId, formatted_extra_data, offer.venue, is_from_private_api=True, offer=offer, ean=body_ean
        )

    for key, value in updates.items():
        if key == "extraData":
            if offer.product:
                continue
        setattr(offer, key, value)
    db.session.add(offer)

    return offer


def create_offer(
    body: offers_schemas.CreateOffer,
    *,
    venue: offerers_models.Venue,
    offerer_address: offerers_models.OffererAddress | None = None,
    provider: providers_models.Provider | None = None,
    is_from_private_api: bool = False,
    venue_provider: providers_models.VenueProvider | None = None,
) -> models.Offer:
    body.extra_data = _format_extra_data(body.subcategory_id, body.extra_data) or {}

    validation.check_offer_withdrawal(
        withdrawal_type=body.withdrawal_type,
        withdrawal_delay=body.withdrawal_delay,
        subcategory_id=body.subcategory_id,
        booking_contact=body.booking_contact,
        provider=provider,
        venue_provider=venue_provider,
    )
    validation.check_offer_subcategory_is_valid(body.subcategory_id)
    validation.check_offer_extra_data(body.subcategory_id, body.extra_data, venue, is_from_private_api, ean=body.ean)
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[body.subcategory_id]
    validation.check_is_duo_compliance(body.is_duo, subcategory)
    validation.check_url_is_coherent_with_subcategory(subcategory, body.url)
    validation.check_can_input_id_at_provider(provider, body.id_at_provider)
    validation.check_can_input_id_at_provider_for_this_venue(venue.id, body.id_at_provider)
    validation.check_offer_name_does_not_contain_ean(body.name)

    fields = body.dict(by_alias=True)

    offerer_address = offerer_address or venue.offererAddress

    if body.url:  # i.e. it is a digital offer
        offerer_address = None

    offer = models.Offer(
        **fields,
        venue=venue,
        offererAddress=offerer_address,
        lastProvider=provider,
        isActive=False,
        validation=models.OfferValidationStatus.DRAFT,
    )
    repository.add_to_session(offer)
    db.session.flush()

    # This log is used for analytics purposes.
    # If you need to make a 'breaking change' of this log, please contact the data team.
    # Otherwise, you will break some dashboards
    logger.info(
        "Offer has been created",
        extra={"offer_id": offer.id, "venue_id": venue.id, "product_id": offer.productId},
        technical_message_id="offer.created",
    )

    update_external_pro(venue.bookingEmail)

    return offer


def get_offerer_address_from_address_body(
    address_body: offerers_schemas.AddressBodyModel | None, venue: offerers_models.Venue
) -> offerers_models.OffererAddress | None:
    if not address_body:
        return None

    if address_body.isVenueAddress:
        return venue.offererAddress

    return offerers_api.get_offerer_address_from_address(venue.managingOffererId, address_body)


def update_offer(
    offer: models.Offer,
    body: offers_schemas.UpdateOffer,
    venue: offerers_models.Venue | None = None,
    offerer_address: offerers_models.OffererAddress | None = None,
    is_from_private_api: bool = False,
) -> models.Offer:
    aliases = set(body.dict(by_alias=True))
    fields = body.dict(by_alias=True, exclude_unset=True)

    # updated using the pro interface
    if body.address:
        offerer_address_from_body = get_offerer_address_from_address_body(address_body=body.address, venue=offer.venue)

        if offerer_address_from_body is not None:
            fields["offererAddress"] = offerer_address_from_body
            fields.pop("address", None)

    should_send_mail = fields.pop("shouldSendMail", False)

    if venue:
        fields["venue"] = venue

    if offerer_address:
        fields["offererAddress"] = offerer_address

    updates = {key: value for key, value in fields.items() if getattr(offer, key) != value}
    updates_set = set(updates)
    if not updates:
        return offer

    if (
        "audioDisabilityCompliant" in updates
        or "mentalDisabilityCompliant" in updates
        or "motorDisabilityCompliant" in updates
        or "visualDisabilityCompliant" in updates
    ):
        validation.check_accessibility_compliance(
            audio_disability_compliant=get_field(offer, updates, "audioDisabilityCompliant", aliases=aliases),
            mental_disability_compliant=get_field(offer, updates, "mentalDisabilityCompliant", aliases=aliases),
            motor_disability_compliant=get_field(offer, updates, "motorDisabilityCompliant", aliases=aliases),
            visual_disability_compliant=get_field(offer, updates, "visualDisabilityCompliant", aliases=aliases),
        )

    if "extraData" in updates or "ean" in updates:
        formatted_extra_data = _format_extra_data(offer.subcategoryId, body.extra_data) or {}
        validation.check_offer_extra_data(
            offer.subcategoryId, formatted_extra_data, offer.venue, is_from_private_api, offer=offer, ean=body.ean
        )

    if "isDuo" in updates:
        is_duo = get_field(offer, updates, "isDuo", aliases=aliases)
        validation.check_is_duo_compliance(is_duo, offer.subcategory)

    if "idAtProvider" in updates:
        id_at_provider = get_field(offer, updates, "idAtProvider", aliases=aliases)
        validation.check_can_input_id_at_provider(offer.lastProvider, id_at_provider)
        validation.check_can_input_id_at_provider_for_this_venue(offer.venueId, id_at_provider, offer.id)

    if "name" in updates:
        name = get_field(offer, updates, "name", aliases=aliases)
        validation.check_offer_name_does_not_contain_ean(name)

    if (
        "withdrawalType" in updates
        or "withdrawalDelay" in updates
        or "withdrawalDetails" in updates
        or "bookingContact" in updates
    ):
        booking_contact = get_field(offer, updates, "bookingContact", aliases=aliases)
        withdrawal_delay = get_field(offer, updates, "withdrawalDelay", aliases=aliases)
        withdrawal_type = get_field(offer, updates, "withdrawalType", aliases=aliases)
        validation.check_offer_withdrawal(
            withdrawal_type=withdrawal_type,
            withdrawal_delay=withdrawal_delay,
            subcategory_id=offer.subcategoryId,
            booking_contact=booking_contact,
            provider=offer.lastProvider,
        )

    validation.check_validation_status(offer)
    if offer.lastProvider is not None:
        validation.check_update_only_allowed_fields_for_offer_from_provider(updates_set, offer.lastProvider)
    if offer.is_soft_deleted():
        raise pc_object.DeletedRecordException()

    changes = {}
    for key, value in updates.items():
        if key == "extraData":
            if offer.product:
                continue
        changes[key] = {"oldValue": getattr(offer, key), "newValue": value}
        setattr(offer, key, value)
    with db.session.no_autoflush:
        validation.check_url_is_coherent_with_subcategory(offer.subcategory, offer.url)
        validation.check_url_and_offererAddress_are_not_both_set(offer.url, offer.offererAddress)
    if offer.isFromAllocine:
        offer.fieldsUpdated = list(set(offer.fieldsUpdated) | updates_set)
    repository.add_to_session(offer)

    # This log is used for analytics purposes.
    # If you need to make a 'breaking change' of this log, please contact the data team.
    # Otherwise, you will break some dashboards
    logger.info(
        "Offer has been updated",
        extra={"offer_id": offer.id, "venue_id": offer.venueId, "product_id": offer.productId, "changes": {**changes}},
        technical_message_id="offer.updated",
    )

    withdrawal_fields = {"bookingContact", "withdrawalDelay", "withdrawalDetails", "withdrawalType"}
    withdrawal_updated = updates_set & withdrawal_fields
    oa_updated = "offererAddress" in updates
    if should_send_mail and (withdrawal_updated or oa_updated):
        transactional_mails.send_email_for_each_ongoing_booking(offer)

    on_commit(
        partial(
            search.async_index_offer_ids,
            [offer.id],
            reason=search.IndexationReason.OFFER_UPDATE,
            log_extra={"changes": updates_set},
        )
    )

    return offer


def batch_update_offers(query: BaseQuery, update_fields: dict, send_email_notification: bool = False) -> None:
    query = query.filter(models.Offer.validation == models.OfferValidationStatus.APPROVED)
    query = query.with_entities(models.Offer.id, models.Offer.venueId).yield_per(2_500)

    offers_count = 0
    found_venue_ids = set()

    logger.info("Batch update of offers: start", extra={"updated_fields": update_fields})

    for chunk in get_chunks(query, chunk_size=2_500):
        raw_offer_ids, raw_venue_ids = zip(*chunk)
        offer_ids = set(raw_offer_ids)
        venue_ids = set(raw_venue_ids)

        offers_count += len(offer_ids)
        found_venue_ids |= set(venue_ids)

        query_to_update = db.session.query(models.Offer).filter(models.Offer.id.in_(offer_ids))
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.flush()

        if "isActive" in update_fields:
            on_commit(
                partial(
                    logger.info,
                    "Offers has been activated" if update_fields["isActive"] else "Offers has been deactivated",
                    technical_message_id="offers.activated" if update_fields["isActive"] else "offers.deactivated",
                    extra={"offer_ids": offer_ids, "venue_ids": venue_ids},
                )
            )

        on_commit(
            partial(
                search.async_index_offer_ids,
                offer_ids,
                reason=search.IndexationReason.OFFER_BATCH_UPDATE,
                log_extra={"changes": set(update_fields.keys())},
            ),
        )

        withdrawal_updated = {"withdrawalDetails", "withdrawalType", "withdrawalDelay"}.intersection(
            update_fields.keys()
        )
        if send_email_notification and withdrawal_updated:
            for offer in query_to_update.all():
                transactional_mails.send_email_for_each_ongoing_booking(offer)

    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    log_extra = {"updated_fields": update_fields, "nb_offers": offers_count, "nb_venues": len(found_venue_ids)}
    logger.info("Batch update of offers: end", extra=log_extra)


def create_event_opening_hours(
    body: offers_schemas.CreateEventOpeningHoursModel,
    offer: models.Offer,
) -> models.EventOpeningHours:
    validation.check_offer_can_have_opening_hours(offer)

    event_opening_hours = models.EventOpeningHours(
        offer=offer,
        startDatetime=body.startDatetime,
        endDatetime=body.endDatetime,
    )
    db.session.add(event_opening_hours)
    db.session.flush()

    for weekday in models.Weekday:
        timeSpans = getattr(body.openingHours, weekday.name)
        if timeSpans:
            weekday_opening_hours = models.EventWeekDayOpeningHours(
                eventOpeningHours=event_opening_hours,
                weekday=weekday,
                timeSpans=timeSpans,
            )
            db.session.add(weekday_opening_hours)
            db.session.flush()

    return event_opening_hours


def activate_future_offers(publication_date: datetime.datetime | None = None) -> list[int]:
    offer_query, future_offer_query = offers_repository.get_offers_by_publication_date(
        publication_date=publication_date
    )
    offer_query = offers_repository.exclude_offers_from_inactive_venue_provider(offer_query)

    with transaction():
        batch_update_offers(offer_query, {"isActive": True})
        future_offer_query.update({"isSoftDeleted": True}, synchronize_session="fetch")

    return [offer.id for offer in offer_query]


def activate_future_offers_and_remind_users() -> None:
    offer_ids = activate_future_offers()

    for offer_id in offer_ids:
        offer = db.session.query(models.Offer).get(offer_id)
        reminders_notifications.notify_users_future_offer_activated(offer=offer)


def set_upper_timespan_of_inactive_headline_offers() -> None:
    inactive_headline_offers = offers_repository.get_inactive_headline_offers()
    for headline_offer in inactive_headline_offers:
        headline_offer.timespan = db_utils.make_timerange(headline_offer.timespan.lower, datetime.datetime.utcnow())
        logger.info(
            "Headline Offer Deactivation",
            extra={
                "analyticsSource": "app-pro",
                "HeadlineOfferId": headline_offer.id,
                "Reason": "Offer is not active anymore, or image has been removed",
            },
            technical_message_id="headline_offer_deactivation",
        )

    db.session.commit()
    search.async_index_offer_ids(
        {headline_offer.offerId for headline_offer in inactive_headline_offers},
        reason=search.IndexationReason.OFFER_REINDEXATION,
    )


def upsert_headline_offer(offer: models.Offer) -> models.HeadlineOffer:
    offerer_id = offer.venue.managingOffererId
    headline_offer = offers_repository.get_current_headline_offer(offerer_id)
    if headline_offer and headline_offer.offerId != offer.id:
        remove_headline_offer(headline_offer)
        logger.info(
            "Headline Offer Deactivation",
            extra={
                "analyticsSource": "app-pro",
                "HeadlineOfferId": headline_offer.id,
                "Reason": "User chose to replace this headline offer by another offer",
            },
            technical_message_id="headline_offer_deactivation",
        )
    new_headline_offer = make_offer_headline(offer)
    return new_headline_offer


def make_offer_headline(offer: models.Offer) -> models.HeadlineOffer:
    offers_validation.check_offerer_is_eligible_for_headline_offers(offer.venue.managingOffererId)
    offers_validation.check_offer_is_eligible_to_be_headline(offer)
    try:
        headline_offer = models.HeadlineOffer(offer=offer, venue=offer.venue, timespan=(datetime.datetime.utcnow(),))
        db.session.add(headline_offer)
        # Note: We use flush and not commit to be compliant with atomic. At this moment,
        # the timespan is a str because the __init__ overloaded method of HeadlineOffer calls
        # make_timerange which transforms timespan into a str using .isoformat. Thus, you will get
        # a TypeError if you try to access the isActive property of this headline_offer object
        # before any session commit. To fix this error, you need to commit your session
        # as the TSRANGE object saves the timespan as a datetime in the database
        db.session.flush()
        on_commit(
            partial(
                search.async_index_offer_ids,
                {offer.id},
                reason=search.IndexationReason.OFFER_REINDEXATION,
            ),
        )
    except sa_exc.IntegrityError as error:
        if "exclude_offer_timespan" in str(error.orig):
            raise exceptions.OfferHasAlreadyAnActiveHeadlineOffer
        if "exclude_venue_timespan" in str(error.orig):
            raise exceptions.VenueHasAlreadyAnActiveHeadlineOffer
        raise error

    return headline_offer


def remove_headline_offer(headline_offer: offers_models.HeadlineOffer) -> None:
    try:
        headline_offer.timespan = db_utils.make_timerange(headline_offer.timespan.lower, datetime.datetime.utcnow())
        on_commit(
            partial(
                search.async_index_offer_ids,
                {headline_offer.offerId},
                reason=search.IndexationReason.OFFER_REINDEXATION,
            ),
        )
    except sa_exc.IntegrityError:
        raise exceptions.CannotRemoveHeadlineOffer


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
    *,
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

    if id_at_provider is not None:
        validation.check_can_input_id_at_provider_for_this_stock(offer.id, id_at_provider)

    activation_codes = activation_codes or []
    if activation_codes:
        validation.check_offer_can_have_activation_codes(offer)
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
    *,
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

        # No need to keep an empty stock
        if quantity == 0:
            delete_stock(stock)

    if booking_limit_datetime is not UNCHANGED and booking_limit_datetime != stock.bookingLimitDatetime:
        modifications["bookingLimitDatetime"] = booking_limit_datetime
        validation.check_activation_codes_expiration_datetime_on_stock_edition(
            stock.activationCodes,
            booking_limit_datetime,
        )

    if beginning_datetime not in (UNCHANGED, stock.beginningDatetime):
        modifications["beginningDatetime"] = beginning_datetime

    if id_at_provider not in (UNCHANGED, stock.idAtProviders):
        if id_at_provider is not None:
            validation.check_can_input_id_at_provider_for_this_stock(
                stock.offer.id,
                id_at_provider,  # type: ignore[arg-type]
                stock.id,
            )
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

    changes = {}
    for model_attr, value in modifications.items():
        changes[model_attr] = {"old_value": getattr(stock, model_attr), "new_value": value}
        setattr(stock, model_attr, value)

    if "beginningDatetime" in modifications:
        finance_api.update_finance_event_pricing_date(stock)

    repository.add_to_session(stock)
    on_commit(
        partial(
            search.async_index_offer_ids,
            [stock.offerId],
            reason=search.IndexationReason.STOCK_UPDATE,
            log_extra={"changes": set(modifications.keys())},
        ),
    )

    # This log is used for analytics purposes.
    # If you need to make a 'breaking change' of this log, please contact the data team.
    # Otherwise, you will break some dashboards
    log_extra_data: dict[str, typing.Any] = {
        "offer_id": stock.offerId,
        "stock_id": stock.id,
        "stock_dnBookedQuantity": stock.dnBookedQuantity,
        "provider_id": editing_provider.id if editing_provider else None,
        "changes": {**changes},
    }
    logger.info("Successfully updated stock", extra=log_extra_data, technical_message_id="stock.updated")

    return stock, "beginningDatetime" in modifications


def handle_stocks_edition(edited_stocks: list[tuple[models.Stock, bool]]) -> None:
    for stock, is_beginning_datetime_updated in edited_stocks:
        if is_beginning_datetime_updated:
            handle_event_stock_beginning_datetime_update(stock)


def handle_event_stock_beginning_datetime_update(stock: models.Stock) -> None:
    bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
    _notify_pro_upon_stock_edit_for_event_offer(stock, bookings)
    _notify_beneficiaries_upon_stock_edit(stock, bookings)  # TODO: (tcoudray-pass, 16/04/2025) rename this function


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
    publication_date: datetime.datetime | None = None,
) -> models.Offer:
    finalization_date = datetime.datetime.now(datetime.timezone.utc)

    if not offer.finalizationDatetime:
        offer.finalizationDatetime = finalization_date

    publication_date = _format_publication_date(publication_date, offer.venue.timezone)
    validation.check_publication_date(offer, publication_date)

    if ean := offer.ean:
        validation.check_other_offer_with_ean_does_not_exist(ean, offer.venue, offer.id)

    if publication_date is not None:  # i.e. pro user schedules the publication in the future
        offer.isActive = False
        offer.publicationDatetime = publication_date
        offer.bookingAllowedDatetime = publication_date

        # (tcoudray-pass, 23/05/2025) Remove when publicationDatetime is used instead of future_offer
        future_offer = models.FutureOffer(offerId=offer.id, publicationDate=publication_date)
        db.session.add(future_offer)
    else:  # i.e. pro user publishes the offer right away
        offer.isActive = True
        offer.publicationDatetime = finalization_date
        offer.bookingAllowedDatetime = finalization_date

        # (tcoudray-pass, 23/05/2025) Remove when publicationDatetime is used instead of future_offer
        if offer.publicationDate:
            offers_repository.delete_future_offer(offer.id)

        on_commit(partial(search.async_index_offer_ids, [offer.id], reason=search.IndexationReason.OFFER_PUBLICATION))
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
            try:
                bookings_api.mark_as_unused(booking)
            except booking_exceptions.BookingIsAlreadyRefunded:
                pass  # should not happen (race condition)
    return bookings


def _delete_stock(stock: models.Stock, author_id: int | None = None, user_connect_as: bool | None = None) -> None:
    stock.isSoftDeleted = True
    repository.save(stock)

    # the algolia sync for the stock will happen within this function
    cancelled_bookings = bookings_api.cancel_bookings_from_stock_by_offerer(stock, author_id, user_connect_as)

    # This log is used for analytics purposes.
    # If you need to make a 'breaking change' of this log, please contact the data team.
    # Otherwise, you will break some dashboards
    logger.info(
        "Deleted stock and cancelled its bookings",
        extra={
            "stock": stock.id,
            "bookings": [b.id for b in cancelled_bookings],
            "author_id": author_id,
            "user_connect_as": bool(user_connect_as),
        },
        technical_message_id="stock.deleted",
    )
    if cancelled_bookings:
        for booking in cancelled_bookings:
            transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email(booking)
        transactional_mails.send_booking_cancellation_confirmation_by_pro_email(cancelled_bookings)
        if not feature.FeatureToggle.WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION.is_active():
            on_commit(
                partial(
                    push_notification_job.send_cancel_booking_notification.delay,
                    [booking.id for booking in cancelled_bookings],
                )
            )

    on_commit(
        partial(
            search.async_index_offer_ids,
            [stock.offerId],
            reason=search.IndexationReason.STOCK_DELETION,
        )
    )


def delete_stock(stock: models.Stock, author_id: int | None = None, user_connect_as: bool | None = None) -> None:
    validation.check_stock_is_deletable(stock)
    _delete_stock(stock, author_id, user_connect_as)


def create_mediation(
    user: users_models.User | None,
    offer: models.Offer,
    credit: str | None,
    image_as_bytes: bytes,
    *,
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
        db.session.query(models.Mediation)
        .filter(models.Mediation.offerId == offer.id)
        .filter(models.Mediation.id != mediation.id)
        .all()
    )
    _delete_mediations_and_thumbs(previous_mediations)

    on_commit(
        partial(
            search.async_index_offer_ids,
            [offer.id],
            reason=search.IndexationReason.MEDIATION_CREATION,
        ),
    )

    return mediation


def delete_mediations(offer_ids: typing.Collection[int], reindex: bool = True) -> None:
    mediations = db.session.query(models.Mediation).filter(models.Mediation.offerId.in_(offer_ids)).all()

    _delete_mediations_and_thumbs(mediations)

    if reindex:
        on_commit(
            partial(
                search.async_index_offer_ids,
                offer_ids,
                reason=search.IndexationReason.MEDIATION_DELETION,
            ),
        )


def _delete_mediations_and_thumbs(mediations: list[models.Mediation]) -> None:
    for mediation in mediations:
        try:
            for thumb_index in range(1, mediation.thumbCount + 1):
                suffix = str(thumb_index - 1) if thumb_index > 1 else ""
                remove_thumb(mediation, storage_id_suffix=suffix)
        except Exception as exception:
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
    if (not ean and not visa) or not criterion_ids:
        return False

    query = db.session.query(models.Product)
    if ean:
        ean = ean.replace("-", "").replace(" ", "")
        query = query.filter(models.Product.ean == ean)
    if visa:
        query = query.filter(models.Product.extraData["visa"].astext == visa)

    products = query.all()
    if not products:
        return False

    offer_ids_query = (
        db.session.query(models.Offer)
        .filter(models.Offer.productId.in_(p.id for p in products), models.Offer.isActive.is_(True))
        .with_entities(models.Offer.id)
    )
    offer_ids = {offer_id for (offer_id,) in offer_ids_query.all()}

    if not offer_ids:
        return False

    values: list[dict[str, int]] = []
    for criterion_id in criterion_ids:
        logger.info("Adding criterion %s to %d offers", criterion_id, len(offer_ids))
        values += [{"offerId": offer_id, "criterionId": criterion_id} for offer_id in offer_ids]

    db.session.execute(
        insert(criteria_models.OfferCriterion)
        .values(values)
        .on_conflict_do_nothing(index_elements=["offerId", "criterionId"])
    )
    db.session.flush()

    on_commit(
        partial(
            search.async_index_offer_ids,
            offer_ids,
            reason=search.IndexationReason.CRITERIA_LINK,
            log_extra={"criterion_ids": criterion_ids},
        ),
    )

    return True


def reject_inappropriate_products(
    eans: list[str],
    author: users_models.User | None,
    rejected_by_fraud_action: bool = False,
    send_booking_cancellation_emails: bool = True,
) -> bool:
    products = (
        db.session.query(models.Product)
        .filter(
            models.Product.ean.in_(eans),
            models.Product.idAtProviders.is_not(None),
            models.Product.gcuCompatibilityType != models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
        )
        .all()
    )

    if not products:
        return False
    product_ids = [product.id for product in products]
    offers_query = db.session.query(models.Offer).filter(
        sa.or_(
            models.Offer.productId.in_(product_ids),
            models.Offer.ean.in_(eans),
        ),
        models.Offer.validation != models.OfferValidationStatus.REJECTED,
    )

    offers = offers_query.options(sa_orm.joinedload(models.Offer.stocks).joinedload(models.Stock.bookings)).all()

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
        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()
    except Exception as exception:
        if is_managed_transaction():
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
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
                    reason=BookingCancellationReasons.FRAUD_INAPPROPRIATE,
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
        db.session.query(users_models.Favorite).filter(users_models.Favorite.offerId.in_(offer_ids)).delete(
            synchronize_session=False
        )
        on_commit(
            partial(
                search.async_index_offer_ids,
                offer_ids,
                reason=search.IndexationReason.PRODUCT_REJECTION,
                log_extra={"eans": eans},
            ),
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
        db.session.query(models.OfferValidationRule)
        .options(sa_orm.joinedload(models.OfferValidationSubRule, models.OfferValidationRule.subRules))
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
        offer_ids = [offer_id for (offer_id,) in offers.with_entities(models.Offer.id)]

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
    except sa_exc.IntegrityError as error:
        if error.orig.pgcode == UNIQUE_VIOLATION:
            raise exceptions.OfferAlreadyReportedError() from error
        if error.orig.pgcode == CHECK_VIOLATION:
            raise exceptions.ReportMalformed() from error
        raise

    transactional_mails.send_email_reported_offer_by_user(user, offer, reason, custom_reason)


def get_shows_remaining_places_from_provider(provider_class: str | None, offer: models.Offer) -> dict[str, int]:
    match provider_class:
        case "CDSStocks":
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
            film_id = cinema_providers_utils.get_boost_or_cgr_or_ems_film_id_from_uuid(offer.idAtProvider)
            if not film_id:
                return {}
            return external_bookings_api.get_movie_stocks(offer.venueId, film_id)
        case "CGRStocks":
            cgr_allocine_film_id = cinema_providers_utils.get_boost_or_cgr_or_ems_film_id_from_uuid(offer.idAtProvider)
            if not cgr_allocine_film_id:
                return {}
            return external_bookings_api.get_movie_stocks(offer.venueId, cgr_allocine_film_id)
        case "EMSStocks":
            film_id = cinema_providers_utils.get_boost_or_cgr_or_ems_film_id_from_uuid(offer.idAtProvider)
            if not film_id:
                return {}
            return external_bookings_api.get_movie_stocks(offer.venueId, film_id)
    raise ValueError(f"Unknown Provider: {provider_class}")


def _should_try_to_update_offer_stock_quantity(offer: models.Offer) -> bool:
    # The offer is to update only if it is a cinema offer, and if the venue has a cinema provider
    if offer.subcategory.id != subcategories.SEANCE_CINE.id:
        return False

    if not offer.lastProviderId:  # Manual offer
        return False

    offer_venue_providers = offer.venue.venueProviders
    for venue_provider in offer_venue_providers:
        if venue_provider.isFromCinemaProvider:
            return True

    return False


def update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer: models.Offer) -> None:
    if not _should_try_to_update_offer_stock_quantity(offer):
        return
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
        # TODO: (lixxday, 29/05/2024): remove this try/catch when the function is no longer called directly in GET /offer route
        logger.exception(
            "Failed to get shows remaining places from provider",
            extra={"offer": offer.id, "provider": venue_provider.provider.localClass, "error": e},
        )
        return
    except Exception as e:
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
            except sa_exc.InternalError:
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
    db.session.flush()
    return product


def fetch_or_update_product_with_titelive_data(titelive_product: models.Product) -> models.Product:
    product = db.session.query(models.Product).filter_by(idAtProviders=titelive_product.idAtProviders).one_or_none()
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
        product.extraData.pop("ean", None)

    return product


def batch_delete_draft_offers(query: BaseQuery) -> None:
    offer_ids = [id_ for (id_,) in query.with_entities(models.Offer.id)]
    filters = (models.Offer.validation == models.OfferValidationStatus.DRAFT, models.Offer.id.in_(offer_ids))
    db.session.query(models.Mediation).filter(models.Mediation.offerId == models.Offer.id).filter(*filters).delete(
        synchronize_session=False
    )
    db.session.query(criteria_models.OfferCriterion).filter(
        criteria_models.OfferCriterion.offerId == models.Offer.id,
        *filters,
    ).delete(synchronize_session=False)
    db.session.query(models.ActivationCode).filter(
        models.ActivationCode.stockId == models.Stock.id,
        models.Stock.offerId == models.Offer.id,
        *filters,
    ).delete(synchronize_session=False)
    db.session.query(models.Stock).filter(models.Stock.offerId == models.Offer.id).filter(*filters).delete(
        synchronize_session=False
    )
    db.session.query(models.Offer).filter(*filters).delete(synchronize_session=False)
    db.session.flush()


def batch_delete_stocks(
    stocks_to_delete: list[models.Stock], author_id: int | None, user_connect_as: bool | None
) -> None:
    # We want to check that all stocks can be deleted first
    for stock in stocks_to_delete:
        validation.check_stock_is_deletable(stock)

    for stock in stocks_to_delete:
        _delete_stock(stock, author_id, user_connect_as)


def get_or_create_label(label: str, venue: offerers_models.Venue) -> models.PriceCategoryLabel:
    price_category_label = db.session.query(models.PriceCategoryLabel).filter_by(label=label, venue=venue).one_or_none()
    if not price_category_label:
        return models.PriceCategoryLabel(label=label, venue=venue)
    return price_category_label


def create_price_category(
    offer: models.Offer,
    label: str,
    price: decimal.Decimal,
    id_at_provider: str | None = None,
) -> models.PriceCategory:
    validation.check_stock_price(price, offer)

    if id_at_provider is not None:
        validation.check_can_input_id_at_provider_for_this_price_category(offer.id, id_at_provider)

    price_category_label = get_or_create_label(label, offer.venue)
    created_price_category = models.PriceCategory(
        offer=offer, price=price, priceCategoryLabel=price_category_label, idAtProvider=id_at_provider
    )
    repository.add_to_session(created_price_category)
    return created_price_category


def edit_price_category(
    offer: models.Offer,
    price_category: models.PriceCategory,
    *,
    label: str | T_UNCHANGED = UNCHANGED,
    price: decimal.Decimal | T_UNCHANGED = UNCHANGED,
    editing_provider: providers_models.Provider | None = None,
    id_at_provider: str | None | T_UNCHANGED = UNCHANGED,
) -> models.PriceCategory:
    validation.check_price_category_is_updatable(price_category, editing_provider)

    if price is not UNCHANGED and price != price_category.price:
        validation.check_stock_price(price, offer, old_price=price_category.price)
        price_category.price = price

    if label is not UNCHANGED and label != price_category.label:
        price_category_label = get_or_create_label(label, offer.venue)
        price_category.priceCategoryLabel = price_category_label

    if id_at_provider is not UNCHANGED and id_at_provider != price_category.idAtProvider:
        if id_at_provider is not None:
            validation.check_can_input_id_at_provider_for_this_price_category(
                offer.id, id_at_provider, price_category.id
            )
        price_category.idAtProvider = id_at_provider

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
    db.session.flush()


def approves_provider_product_and_rejected_offers(ean: str) -> None:
    product = (
        db.session.query(models.Product)
        .filter(
            models.Product.gcuCompatibilityType == models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
            models.Product.ean == ean,
            models.Product.idAtProviders.is_not(None),
        )
        .one_or_none()
    )

    if not product:
        raise exceptions.ProductNotFound()

    offer_ids = []
    try:
        with transaction():
            product.gcuCompatibilityType = models.GcuCompatibilityType.COMPATIBLE
            db.session.add(product)

            offers_query = (
                db.session.query(models.Offer)
                .filter(
                    models.Offer.productId == product.id,
                    models.Offer.validation == models.OfferValidationStatus.REJECTED,
                    models.Offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
                )
                .options(sa_orm.load_only(models.Offer.id))
            )

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
        db.session.query(models.Stock)
        .with_entities(
            sa.func.min(models.Stock.beginningDatetime),
            sa.func.max(models.Stock.beginningDatetime),
            sa.func.count(models.Stock.id),
            sa.case(
                (
                    db.session.query(models.Stock)
                    .filter(
                        models.Stock.quantity == None,
                        models.Stock.isSoftDeleted.is_(False),
                        models.Stock.offerId == offer_id,
                    )
                    .exists(),
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


def check_can_move_event_offer(offer: models.Offer) -> list[offerers_models.Venue]:
    if not offer.isEvent:
        raise exceptions.OfferIsNotEvent()

    count_past_stocks = (
        db.session.query(models.Stock)
        .with_entities(models.Stock.id)
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
        db.session.query(bookings_models.Booking)
        .with_entities(bookings_models.Booking.id)
        .join(bookings_models.Booking.stock)
        .filter(models.Stock.offerId == offer.id, bookings_models.Booking.isReimbursed)
        .count()
    )
    if count_reimbursed_bookings > 0:
        raise exceptions.OfferHasReimbursedBookings(count_reimbursed_bookings)

    venues_choices = offerers_repository.get_offerers_venues_with_pricing_point(offer.venue)
    if not venues_choices:
        raise exceptions.NoDestinationVenue()
    return venues_choices


def check_can_move_offer(offer: models.Offer) -> list[offerers_models.Venue]:
    venues_choices = offerers_repository.get_offerers_venues_with_pricing_point(
        offer.venue,
        include_without_pricing_points=True,
        only_similar_pricing_points=True,
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


# WARNING: this is WIP, do not use it yet
def move_offer(
    offer: models.Offer,
    destination_venue: offerers_models.Venue,
) -> None:
    if not feature.FeatureToggle.VENUE_REGULARIZATION.is_active():
        raise NotImplementedError("Activate VENUE_REGULARIZATION to use this feature")

    offer_id = offer.id
    original_venue = offer.venue

    venue_choices = check_can_move_offer(offer)

    if destination_venue not in venue_choices:
        raise exceptions.ForbiddenDestinationVenue()

    bookings_ids = (
        db.session.query(bookings_models.Booking)
        .with_entities(bookings_models.Booking.id)
        .join(bookings_models.Booking.stock)
        .filter(models.Stock.offerId == offer.id)
    )
    bookings = db.session.query(bookings_models.Booking).filter(bookings_models.Booking.id.in_(bookings_ids))

    # After offer is moved, price categories must remain linked to labels defined for the related venue.
    # Extra SQL queries to avoid multiplying the number of rows in case of many labels
    original_price_category_labels = {price_category.priceCategoryLabel for price_category in offer.priceCategories}
    labels_mapping = {
        price_category_label: _get_or_create_same_price_category_label(destination_venue, price_category_label)
        for price_category_label in original_price_category_labels
    }
    with transaction():
        # Use a different OA if the offer uses the venue's OA
        if offer.offererAddress and offer.offererAddress == original_venue.offererAddress:
            destination_oa = offerers_api.get_or_create_offerer_address(
                original_venue.managingOffererId, original_venue.offererAddress.addressId, original_venue.common_name
            )
            db.session.add(destination_oa)
            offer.offererAddress = destination_oa

        offer.venue = destination_venue
        db.session.add(offer)

        for price_category in offer.priceCategories:
            price_category.priceCategoryLabel = labels_mapping[price_category.priceCategoryLabel]
            db.session.add(price_category)

        bookings.update({"venueId": destination_venue.id}, synchronize_session=False)

    on_commit(
        partial(
            search.async_index_offer_ids,
            {offer_id},
            reason=search.IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"venueId"}},
        )
    )


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
        db.session.query(bookings_models.Booking)
        .join(bookings_models.Booking.stock)
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
            sa_orm.load_only(bookings_models.Booking.status),
            sa_orm.contains_eager(bookings_models.Booking.finance_events).load_only(finance_models.FinanceEvent.status),
            sa_orm.contains_eager(bookings_models.Booking.pricings).load_only(
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

    on_commit(
        partial(
            search.async_index_offer_ids,
            {offer_id},
            reason=search.IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"venueId"}},
        )
    )

    if notify_beneficiary:
        transactional_mails.send_email_for_each_ongoing_booking(offer)


def update_used_stock_price(
    stock: models.Stock, new_price: float | None = None, price_percent: decimal.Decimal | None = None
) -> None:
    if not stock.offer.isEvent:
        raise ValueError("Only stocks associated with an event offer can be edited with used bookings")
    if (new_price is None) == (price_percent is None):
        raise ValueError("One of [new_price, price_percent] is mandatory")

    if new_price:
        stock.price = new_price
        db.session.query(bookings_models.Booking).filter(
            bookings_models.Booking.stockId == stock.id,
        ).update({bookings_models.Booking.amount: func.least(new_price, bookings_models.Booking.amount)})
    elif price_percent:
        stock.price = round(stock.price * price_percent, 2)
        db.session.query(bookings_models.Booking).filter(
            bookings_models.Booking.stockId == stock.id,
        ).update({bookings_models.Booking.amount: bookings_models.Booking.amount * price_percent})

    first_finance_event = (
        db.session.query(finance_models.FinanceEvent)
        .join(bookings_models.Booking, finance_models.FinanceEvent.booking)
        .filter(
            finance_models.FinanceEvent.status != finance_models.FinanceEventStatus.CANCELLED,
            bookings_models.Booking.stockId == stock.id,
        )
        .order_by(
            finance_models.FinanceEvent.pricingOrderingDate,
            finance_models.FinanceEvent.id,
        )
        .options(
            sa_orm.joinedload(finance_models.FinanceEvent.booking),
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

    existing_product_with_allocine_id = (
        offers_repository.get_movie_product_by_allocine_id(movie.allocine_id) if movie.allocine_id else None
    )
    existing_product_with_visa = offers_repository.get_movie_product_by_visa(movie.visa) if movie.visa else None

    with transaction():
        existing_product = existing_product_with_allocine_id or existing_product_with_visa
        if (
            existing_product_with_allocine_id
            and existing_product_with_visa
            and existing_product_with_allocine_id.id != existing_product_with_visa.id
        ):
            logger.info(
                "Merging movie products %d (to keep) and %d (to delete)",
                existing_product_with_allocine_id.id,
                existing_product_with_visa.id,
                extra={"allocine_id": movie.allocine_id, "visa": movie.visa},
            )
            existing_product = offers_repository.merge_products(
                existing_product_with_allocine_id, existing_product_with_visa
            )
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


def update_event_opening_hours(
    event: offers_models.EventOpeningHours, update_body: offers_schemas.UpdateEventOpeningHoursModel
) -> None:
    """Update an event opening hours information: start and end dates,
    opening hours.

    Start and end dates updates are trivial. The opening hours part is
    a little bit more complicated. The update body must contain the
    whole opening hours update. This means that:
        * an unknown day should be removed from the event opening hours;
        * an existing day will overwrite existing timespans;
        * a new day (unknown to the event opening hours) will create a new
        database object.

    Warning: no update nor insert will be committed by this function.
    """
    offers_validation.check_event_opening_hours_can_be_updated(event.offer, event, update_body)

    if update_body.startDatetime:
        event.startDatetime = update_body.startDatetime

    if update_body.endDatetime:
        event.endDatetime = update_body.endDatetime

    if update_body.openingHours:
        existing_days_with_opening_hours = {day.weekday.value for day in event.weekDayOpeningHours}
        new_opening_hours = update_body.openingHours.dict()

        to_remove = {day for day, ts in new_opening_hours.items() if not ts}
        to_update = {day for day, ts in new_opening_hours.items() if ts and day in existing_days_with_opening_hours}
        to_create = new_opening_hours.keys() - to_remove - to_update

        for weekday_opening_hours in event.weekDayOpeningHours:
            weekday = weekday_opening_hours.weekday.value

            if weekday in to_remove:
                db.session.delete(weekday_opening_hours)

            elif weekday in to_update:
                weekday_opening_hours.timeSpans = new_opening_hours[weekday]

        for weekday in to_create:
            time_spans = new_opening_hours[weekday]
            db.session.add(
                models.EventWeekDayOpeningHours(
                    eventOpeningHours=event, weekday=models.Weekday[weekday], timeSpans=time_spans
                )
            )


def delete_event_opening_hours(event_opening_hours: offers_models.EventOpeningHours) -> None:
    """Delete an offer's opening hours and cancel its related bookings.

    No database row in really deleted, it is marked as soft deleted instead.
    Same for any of its offer's stocks.
    """
    event_opening_hours.isSoftDeleted = True
    for stock in event_opening_hours.offer.stocks:
        stock.isSoftDeleted = True

        for booking in stock.bookings:
            try:
                bookings_api.cancel_booking_by_offerer(booking)
            except (bookings_exceptions.BookingIsAlreadyCancelled, bookings_exceptions.BookingIsAlreadyRefunded):
                # this should not happen but it can safely be ignored since
                # the main goal here is to block the user from using its
                # booking.
                continue
            except bookings_exceptions.BookingIsAlreadyUsed:
                raise exceptions.EventOpeningHoursException(
                    field="booking", msg=f"booking #{booking.id} is already used, it cannot be cancelled"
                )


def delete_offers_stocks_related_objects(offer_ids: typing.Collection[int]) -> None:
    stock_ids_query = db.session.query(models.Stock.id).filter(models.Stock.offerId.in_(offer_ids))
    stock_ids = [row[0] for row in stock_ids_query]

    for chunk in get_chunks(stock_ids, chunk_size=128):
        models.ActivationCode.query.filter(
            models.ActivationCode.stockId.in_(chunk),
            # All bookingId should be None if venue_has_bookings is False,
            # keep condition to get an exception otherwise
            models.ActivationCode.bookingId.is_(None),
        ).delete(synchronize_session=False)


def delete_offers_related_objects(offer_ids: typing.Collection[int]) -> None:
    delete_offers_stocks_related_objects(offer_ids)

    related_models = [
        models.Stock,
        users_models.Favorite,
        models.Mediation,
        models.OfferReport,
        finance_models.CustomReimbursementRule,
        models.EventOpeningHours,
    ]

    for model in related_models:
        model.query.filter(model.offerId.in_(offer_ids)).delete(synchronize_session=False)  # type: ignore[attr-defined]

    delete_mediations(offer_ids, reindex=False)


def _format_error_extra(error: Exception, ids: typing.Collection[int]) -> dict:
    return {"ids": ids, "error": str(error)}


def _format_db_error_extra(error: sa.exc.IntegrityError, ids: typing.Collection[int]) -> dict:
    extra = _format_error_extra(error, ids)

    with suppress(Exception):
        extra["details"] = {
            "orig": str(error.orig),
            "code": error.code,
            "params": error.params,
        }

    return extra


@atomic()
def delete_offers_and_all_related_objects(offer_ids: typing.Collection[int], offer_chunk_size: int = 16) -> None:
    """Delete a set of offers and all of their related objects and
    unindex them all. Each removal is done by batch which runs inside
    a transaction.

    Notes:
        The `offer_chunk_size` should be bigger if offers have no or
        very few related objects and kept quite small otherwise
        because of the transaction that should not last long.
    """

    def delete_offers_related_objects_round(idx: int, chunk: typing.Collection[int]) -> None:
        start = time.time()

        delete_offers_related_objects(chunk)

        unindex_offers_partial = functools.partial(search.unindex_offer_ids, chunk)
        on_commit(unindex_offers_partial)

        models.Offer.query.filter(models.Offer.id.in_(chunk)).delete(synchronize_session=False)
        db.session.flush()

        log_extra = {"round": idx, "offers_count": len(chunk), "time_spent": str(time.time() - start)}
        logger.info("delete offers and related objects: round %d, end", idx, extra=log_extra)

    for idx, chunk in enumerate(get_chunks(offer_ids, chunk_size=offer_chunk_size)):
        try:
            with atomic():
                delete_offers_related_objects_round(idx, chunk)
        except sa.exc.IntegrityError as err:
            extra = _format_db_error_extra(err, chunk)
            logger.error("delete_offers_and_all_related_objects: error", extra=extra)
            continue
        except Exception as err:
            extra = _format_error_extra(err, chunk)
            logger.error("delete_offers_and_all_related_objects: error", extra=extra)
            continue


def delete_unbookable_unbooked_old_offers(
    min_id: int = 0,
    max_id: int | None = None,
    query_batch_size: int = 5_000,
    filter_batch_size: int = 2_500,
    delete_batch_size: int = 32,
) -> None:
    """Delete all unusable offers.

    This means offers that:
        * have been updated more than a year ago;
        * (AND) are not bookable (no available stock);
        * (AND) have never been booked.

    Each offer should be deleted, with its stocks and all related objects.
    Each offer should also be unindexed.
    """
    start = time.time()
    log_extra = {
        "min_id": min_id,
        "max_id": max_id,
        "query_batch_size": query_batch_size,
        "filter_batch_size": filter_batch_size,
        "delete_batch_size": delete_batch_size,
    }
    logger.info("delete_unbookable_unbooked_unmodified_old_offers start", extra=log_extra)

    count = 0

    query = offers_repository.get_unbookable_unbooked_old_offer_ids(min_id, max_id, batch_size=query_batch_size)
    for idx, chunk in enumerate(get_chunks(query, chunk_size=filter_batch_size)):
        inner_start = time.time()

        delete_offers_and_all_related_objects(chunk, delete_batch_size)

        count += len(chunk)

        extra = {
            "round": idx,
            "time_spent": time.time() - inner_start,
            "offers_count": len(chunk),
            "min_id": min(chunk),
            "max_id": max(chunk),
        }
        logger.info("delete_unbookable_unbooked_unmodified_old_offers round %d: end", idx, extra=extra)

        for offer_id in chunk:
            log_msg = "deleted unbookable unbooked offers ids"
            technical_id = "unbookable_unbooked_offers_deleted"
            logger.info(log_msg, technical_message_id=technical_id, extra={"offer_id": offer_id})

    log_extra["time_spent"] = time.time() - start  # type: ignore[assignment]
    log_extra["deleted_offers_count"] = count
    logger.info("delete_unbookable_unbooked_unmodified_old_offers end", extra=log_extra)


def get_existing_offers(
    ean_to_create_or_update: set[str],
    venue: offerers_models.Venue,
) -> list[offers_models.Offer]:
    subquery = (
        db.session.query(
            sa.func.max(offers_models.Offer.id).label("max_id"),
        )
        .filter(offers_models.Offer.isEvent == False)
        .filter(offers_models.Offer.venue == venue)
        .filter(offers_models.Offer.ean.in_(ean_to_create_or_update))
        .group_by(
            offers_models.Offer.ean,
            offers_models.Offer.venueId,
        )
        .subquery()
    )

    return (
        offers_utils.retrieve_offer_relations_query(db.session.query(offers_models.Offer))
        .join(subquery, offers_models.Offer.id == subquery.c.max_id)
        .all()
    )


def create_product(
    venue: offerers_models.Venue,
    body: individual_offers_v1_serialization.ProductOfferCreation,
    offerer_address: offerers_models.OffererAddress | None,
    api_key: ApiKey,
) -> offers_models.Offer:
    try:
        offer_body = offers_schemas.CreateOffer(
            name=body.name,
            subcategoryId=body.category_related_fields.subcategory_id,
            audioDisabilityCompliant=body.accessibility.audio_disability_compliant,
            mentalDisabilityCompliant=body.accessibility.mental_disability_compliant,
            motorDisabilityCompliant=body.accessibility.motor_disability_compliant,
            visualDisabilityCompliant=body.accessibility.visual_disability_compliant,
            bookingContact=body.booking_contact,
            bookingEmail=body.booking_email,
            description=body.description,
            externalTicketOfficeUrl=body.external_ticket_office_url,
            ean=(body.category_related_fields.ean if hasattr(body.category_related_fields, "ean") else None),
            extraData=individual_offers_v1_serialization.deserialize_extra_data(
                body.category_related_fields, venue_id=venue.id
            ),
            idAtProvider=body.id_at_provider,
            isDuo=body.enable_double_bookings,
            url=(
                body.location.url
                if isinstance(body.location, individual_offers_v1_serialization.DigitalLocation)
                else None
            ),
            withdrawalDetails=body.withdrawal_details,
        )  # type: ignore[call-arg]
        created_product = create_offer(
            offer_body,
            venue=venue,
            provider=api_key.provider,
            offerer_address=offerer_address,
        )

        # To create stocks or publishing the offer we need to flush
        # the session to get the offer id
        db.session.flush()
    except sa_exc.IntegrityError as error:
        # a unique constraint violation can only mean that the venueId/idAtProvider
        # already exists
        is_offer_table = error.orig.diag.table_name == offers_models.Offer.__tablename__
        is_unique_constraint_violation = error.orig.pgcode == UNIQUE_VIOLATION
        unique_id_at_provider_venue_id_is_violated = is_offer_table and is_unique_constraint_violation

        if unique_id_at_provider_venue_id_is_violated:
            raise offers_exceptions.ExistingVenueWithIdAtProviderError() from error
        # Other error are unlikely, but we still need to manage them.
        raise offers_exceptions.CreateProductDBError() from error
    except sa_exc.SQLAlchemyError as error:
        raise offers_exceptions.CreateProductDBError() from error

    return created_product


def get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    return (
        db.session.query(offers_models.Product)
        .filter(
            offers_models.Product.ean.in_(ean_to_create),
            offers_models.Product.can_be_synchronized == True,
            offers_models.Product.subcategoryId.in_(offers_constants.ALLOWED_PRODUCT_SUBCATEGORIES),
            # FIXME (cepehang, 2023-09-21) remove these condition when the product table is cleaned up
            offers_models.Product.lastProviderId.is_not(None),
            offers_models.Product.idAtProviders.is_not(None),
        )
        .all()
    )


def create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
    offererAddress: offerers_models.OffererAddress,
) -> offers_models.Offer:
    ean = product.ean

    offer = build_new_offer_from_product(
        venue,
        product,
        id_at_provider=ean,
        provider_id=provider.id,
        offerer_address_id=offererAddress.id,
    )

    offer.audioDisabilityCompliant = venue.audioDisabilityCompliant
    offer.mentalDisabilityCompliant = venue.mentalDisabilityCompliant
    offer.motorDisabilityCompliant = venue.motorDisabilityCompliant
    offer.visualDisabilityCompliant = venue.visualDisabilityCompliant

    offer.isActive = True
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None

    logger.info(
        "models.Offer has been created",
        extra={
            "offer_id": offer.id,
            "venue_id": venue.id,
            "product_id": offer.productId,
        },
        technical_message_id="offer.created",
    )

    return offer


def check_offer_can_be_edited(offer: offers_models.Offer) -> None:
    allowed_product_subcategory_ids = [
        category.id for category in individual_offers_v1_serialization.ALLOWED_PRODUCT_SUBCATEGORIES
    ]
    if offer.subcategoryId not in allowed_product_subcategory_ids:
        raise api_errors.ApiErrors(
            {
                "product.subcategory": [
                    "Only "
                    + ", ".join(
                        (
                            subcategory.id
                            for subcategory in individual_offers_v1_serialization.ALLOWED_PRODUCT_SUBCATEGORIES
                        )
                    )
                    + " products can be edited"
                ]
            }
        )


def upsert_product_stock(
    offer: offers_models.Offer,
    stock_body: individual_offers_v1_serialization.StockEdition | None,
    provider: providers_models.Provider,
) -> None:
    existing_stock = next((stock for stock in offer.activeStocks), None)
    if not stock_body:
        if existing_stock:
            delete_stock(existing_stock)
        return

    # no need to create an empty stock
    if not existing_stock and stock_body.quantity == 0:
        return

    if not existing_stock:
        if stock_body.price is None:
            raise api_errors.ApiErrors({"stock.price": ["Required"]})
        create_stock(
            offer=offer,
            price=finance_utils.cents_to_full_unit(stock_body.price),
            quantity=individual_offers_v1_serialization.deserialize_quantity(stock_body.quantity),
            booking_limit_datetime=stock_body.booking_limit_datetime,
            creating_provider=provider,
        )
        return

    stock_update_body = stock_body.dict(exclude_unset=True)
    price = stock_update_body.get("price", UNCHANGED)

    quantity = individual_offers_v1_serialization.deserialize_quantity(stock_update_body.get("quantity", UNCHANGED))
    new_quantity = quantity + existing_stock.dnBookedQuantity if isinstance(quantity, int) else quantity

    # do not keep empty stocks
    if new_quantity == 0:
        delete_stock(existing_stock)
        return

    edit_stock(
        existing_stock,
        quantity=new_quantity,
        price=(finance_utils.cents_to_full_unit(price) if price != UNCHANGED else UNCHANGED),
        booking_limit_datetime=stock_update_body.get("booking_limit_datetime", UNCHANGED),
        editing_provider=provider,
    )
