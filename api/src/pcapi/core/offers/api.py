import dataclasses
import datetime
import decimal
import difflib
import enum
import functools
import logging
import time
import typing
import uuid
from contextlib import suppress
from functools import partial

import PIL
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask import current_app
from psycopg2.errorcodes import CHECK_VIOLATION
from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from werkzeug.exceptions import BadRequest

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.chronicles.models as chronicles_models
import pcapi.core.criteria.models as criteria_models
import pcapi.core.finance.conf as finance_conf
import pcapi.core.highlights.models as highlights_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.exceptions as offers_exceptions
import pcapi.core.offers.validation as offers_validation
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
import pcapi.core.reactions.models as reactions_models
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.connectors import thumb_storage
from pcapi.connectors import titelive
from pcapi.connectors.serialization.titelive_serializers import TiteliveImage
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import remove_thumb
from pcapi.connectors.titelive import get_new_product_from_ean13
from pcapi.core import search
from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.educational import models as educational_models
from pcapi.core.external import compliance
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.finance import api as finance_api
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
from pcapi.core.search.models import IndexationReason
from pcapi.core.videos import api as videos_api
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.models import pc_object
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils
from pcapi.utils import image_conversion
from pcapi.utils import repository
from pcapi.utils import requests
from pcapi.utils.chunks import get_chunks
from pcapi.utils.custom_keys import get_field
from pcapi.utils.custom_logic import OPERATIONS
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.repository import transaction
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import is_managed_transaction
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit
from pcapi.workers import push_notification_job

from . import exceptions
from . import models
from . import repository as offers_repository
from . import schemas as offers_schemas
from . import validation


logger = logging.getLogger(__name__)

AnyOffer = educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate | models.Offer

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
            formatted_extra_data[field_name] = extra_data.get(field_name)  # type: ignore[literal-required]

    return formatted_extra_data


def create_draft_offer(
    body: offers_schemas.deprecated.PostDraftOfferBodyModel,
    venue: offerers_models.Venue,
    product: offers_models.Product | None = None,
) -> models.Offer:
    validation.check_offer_subcategory_is_valid(body.subcategory_id)
    validation.check_product_for_venue_and_subcategory(product, body.subcategory_id, venue.venueTypeCode)
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[body.subcategory_id]

    body.extra_data = _format_extra_data(body.subcategory_id, body.extra_data) or {}

    validation.check_offer_name_does_not_contain_ean(body.name)
    body_ean = body.extra_data.pop("ean", None)
    validation.check_offer_extra_data(
        body.subcategory_id, body.extra_data, venue, is_from_private_api=True, ean=body_ean
    )
    validation.check_duration_minutes(body.duration_minutes, is_from_private_api=True)

    validation.check_accessibility_compliance(
        audio_disability_compliant=body.audio_disability_compliant,
        mental_disability_compliant=body.mental_disability_compliant,
        motor_disability_compliant=body.motor_disability_compliant,
        visual_disability_compliant=body.visual_disability_compliant,
    )

    fields = {
        key: value for key, value in body.dict(by_alias=True).items() if key not in ("venueId", "callId", "videoUrl")
    }
    fields.update({"ean": body_ean})
    fields.update({"withdrawalDetails": venue.withdrawalDetails})
    fields.update({"isDuo": bool(subcategory and subcategory.is_event and subcategory.can_be_duo)})
    if product:
        fields.pop("extraData", None)
        fields.pop("description", None)
        fields.pop("durationMinutes", None)

    offer = models.Offer(
        **fields,
        venue=venue,
        validation=models.OfferValidationStatus.DRAFT,
        product=product,
    )

    db.session.add(offer)
    db.session.flush()

    update_external_pro(venue.bookingEmail)

    return offer


def update_draft_offer(offer: models.Offer, body: offers_schemas.deprecated.PatchDraftOfferBodyModel) -> models.Offer:
    aliases = set(body.dict(by_alias=True))
    fields = body.dict(by_alias=True, exclude_unset=True)

    if "videoUrl" in fields:
        if new_video_url := fields.pop("videoUrl", None):
            videos_api.upsert_video_and_metadata(new_video_url, offer)
        elif offer.metaData and offer.metaData.videoUrl:
            videos_api.remove_video_data_from_offer_metadata(
                offer.metaData, offer.id, offer.venueId, offer.metaData.videoUrl
            )

    body_ean = body.extra_data.get("ean", None) if body.extra_data else None
    if body_ean:
        fields["ean"] = fields["extraData"].pop("ean")

    # - The offer URL must not be removed if the offer has an online subcategory.
    if offer.url and "url" in body.__fields_set__ and body.url is None:
        offer_subcategory = subcategories.ALL_SUBCATEGORIES_DICT[offer.subcategoryId]
        validation.check_url_is_coherent_with_subcategory(offer_subcategory, None)

    updates = {key: value for key, value in fields.items() if getattr(offer, key) != value}
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

    if body.name:
        validation.check_offer_name_does_not_contain_ean(body.name)

    if "extraData" in updates or "ean" in updates:
        formatted_extra_data = _format_extra_data(offer.subcategoryId, body.extra_data) or {}
        validation.check_offer_extra_data(
            offer.subcategoryId, formatted_extra_data, offer.venue, is_from_private_api=True, offer=offer, ean=body_ean
        )

    if "durationMinutes" in updates:
        duration_minutes = get_field(offer, updates, "durationMinutes", aliases=aliases)
        validation.check_duration_minutes(duration_minutes, is_from_private_api=True)

    changes = {key: {"old": getattr(offer, key), "new": new_value} for key, new_value in updates.items()}
    on_commit(partial(logger.info, "update draft offer", extra={"offer": offer.id, "changes": changes}))

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
    product: offers_models.Product | None = None,
    is_from_private_api: bool = False,
    venue_provider: providers_models.VenueProvider | None = None,
) -> models.Offer:
    """Main entry point to offer creation

    Note:
        For some historical reason this function was only used by public
        API calls and the internal API calls were using another function.
        Both should use the same entrypoint but this is still a work in
        progress since some rules are slightly different.
    """
    body.extra_data = _format_extra_data(body.subcategory_id, body.extra_data) or {}

    if is_from_private_api:
        # TODO(jbaudet): should be ok to remove from this if-block since
        # only internal api calls will pass product as a parameter.
        validation.check_product_for_venue_and_subcategory(product, body.subcategory_id, venue.venueTypeCode)

        # TODO(jbaudet): should be ok to remove from this if-block
        # but let's be sure before doing anything stupid
        validation.check_accessibility_compliance(
            audio_disability_compliant=body.audio_disability_compliant,
            mental_disability_compliant=body.mental_disability_compliant,
            motor_disability_compliant=body.motor_disability_compliant,
            visual_disability_compliant=body.visual_disability_compliant,
        )

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
    # The location (= address/url step) is at the second step of the offer creation workflow,
    # so the portal doesn't send this info during offer creation (but during the next offer update).
    if not is_from_private_api:
        validation.check_url_is_coherent_with_subcategory(subcategory, body.url)
    validation.check_can_input_id_at_provider(provider, body.id_at_provider)
    validation.check_can_input_id_at_provider_for_this_venue(venue.id, body.id_at_provider)
    validation.check_offer_name_does_not_contain_ean(body.name)
    validation.check_duration_minutes(body.duration_minutes, is_from_private_api)

    fields = body.dict(by_alias=True)
    fields.pop("videoUrl", None)

    if is_from_private_api:
        if not body.withdrawal_details:
            fields.update({"withdrawalDetails": venue.withdrawalDetails})

        subcategory = subcategories.ALL_SUBCATEGORIES_DICT[body.subcategory_id]
        fields.update({"isDuo": bool(subcategory and subcategory.is_event and subcategory.can_be_duo)})

        keys_to_remove = {"venueId", "callId"}
        if product:
            keys_to_remove |= {"extraData", "description", "durationMinutes"}

        fields = {k: v for k, v in fields.items() if k not in keys_to_remove}

    offerer_address = offerer_address or venue.offererAddress

    if body.url:  # i.e. it is a digital offer
        offerer_address = None

    offer = models.Offer(
        **fields,
        venue=venue,
        product=product,
        offererAddress=offerer_address,
        lastProvider=provider,
        validation=models.OfferValidationStatus.DRAFT,
        publicationDatetime=None,
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


def get_or_create_offerer_address_from_address_body(
    address_body: offerers_schemas.LocationModel | offerers_schemas.LocationOnlyOnVenueModel | None,
    venue: offerers_models.Venue,
) -> offerers_models.OffererAddress | None:
    if not address_body:
        return None

    if isinstance(address_body, offerers_schemas.LocationOnlyOnVenueModel):
        # TODO (prouzet, 2025-11-20) CLEAN_OA The following condition should not happen after step 4.5
        # but must be kept to avoid duplication before venues have their exclusive location.
        if venue.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION:
            return venue.offererAddress

        # Use the same address as the venue, but offer must not be linked to a VENUE_LOCATION
        return offerers_api.get_or_create_offer_location(
            venue.managingOffererId, venue.offererAddress.addressId, label=venue.common_name
        )

    return offerers_api.get_offer_location_from_address(venue.managingOffererId, address_body)


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
    if body.location:
        offerer_address_from_body = get_or_create_offerer_address_from_address_body(
            address_body=body.location, venue=offer.venue
        )

        if offerer_address_from_body is not None:
            fields["offererAddress"] = offerer_address_from_body
            fields.pop("location", None)

    should_send_mail = fields.pop("shouldSendMail", False)

    if venue:
        fields["venue"] = venue

    if offerer_address:
        fields["offererAddress"] = offerer_address

    if "videoUrl" in fields:
        if new_video_url := fields.pop("videoUrl", None):
            videos_api.upsert_video_and_metadata(new_video_url, offer)
        elif offer.metaData and offer.metaData.videoUrl:
            videos_api.remove_video_data_from_offer_metadata(
                offer.metaData, offer.id, offer.venueId, offer.metaData.videoUrl
            )
            logger.info(
                "Video has been deleted from offer",
                extra={"offer_id": offer.id, "venue_id": offer.venueId, "video_url": offer.metaData.videoUrl},
                technical_message_id="offer.video.deleted",
            )

    updates = {key: value for key, value in fields.items() if getattr(offer, key) != value}
    updates_set = set(updates)
    if not updates:
        return offer

    if "bookingAllowedDatetime" in updates:
        bookingAllowedDatetime = get_field(offer, updates, "bookingAllowedDatetime", aliases=aliases)
        if not bookingAllowedDatetime or (bookingAllowedDatetime <= get_naive_utc_now()):
            reminders_notifications.notify_users_offer_is_bookable(offer)

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
        if name is None:
            raise exceptions.OfferException({"name": ["cannot be null"]})
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

    try:
        updates["ean"] = updates["extraData"].pop("ean")

        # TODO(jbaudet - 11/2025): remove this whole try/except in a
        # couple of weeks, after checking that this warning never
        # appears.
        # Caller should use body.ean instead of body.extra_data["ean"]
        # This seems to be ok today, but... lets wait a little bit before
        # doing anything stupid.
        logger.warning(
            "update_offer: extracting EAN from extraData (use body.ean instead)",
            extra={"offer": offer.id, "ean": updates["ean"]},
        )
    except (KeyError, AttributeError):
        pass

    # - The offer URL must not be removed if the offer has an online subcategory.
    if offer.url and "url" in body.__fields_set__ and body.url is None:
        offer_subcategory = subcategories.ALL_SUBCATEGORIES_DICT[offer.subcategoryId]
        validation.check_url_is_coherent_with_subcategory(offer_subcategory, None)

    if "subcategoryId" in updates and offer.status != models.OfferStatus.DRAFT:
        raise offers_exceptions.UnallowedUpdate("subcategoryId")

    if "durationMinutes" in updates:
        duration_minutes = get_field(offer, updates, "durationMinutes", aliases=aliases)
        validation.check_duration_minutes(duration_minutes, is_from_private_api)

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

        # the creation process is splitted into several steps. URL and
        # address might be set only in the end. Therefore, this
        # validation is meaningless until the offer has been finalized.
        if offer.status != models.OfferStatus.DRAFT:
            validation.check_url_and_offererAddress_are_not_both_set(offer.url, offer.offererAddress)
    if offer.isFromAllocine:
        offer.fieldsUpdated = list(set(offer.fieldsUpdated) | updates_set)
    repository.add_to_session(offer)

    # This log is used for analytics purposes.
    # If you need to make a 'breaking change' of this log, please contact the data team.
    # Otherwise, you will break some dashboards
    on_commit(
        partial(
            logger.info,
            "Offer has been updated",
            extra={
                "offer_id": offer.id,
                "venue_id": offer.venueId,
                "product_id": offer.productId,
                "changes": {**changes},
            },
            technical_message_id="offer.updated",
        )
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
            reason=IndexationReason.OFFER_UPDATE,
            log_extra={"changes": updates_set},
        )
    )

    return offer


def batch_update_offers(
    query: sa_orm.Query,
    update_fields: dict | None = None,
    activate: bool | None = None,
    send_email_notification: bool = False,
) -> set[int]:
    query = query.filter(models.Offer.validation == models.OfferValidationStatus.APPROVED)
    query = query.with_entities(models.Offer.id, models.Offer.venueId).yield_per(2_500)

    updated_offer_ids = set()
    found_venue_ids = set()

    if update_fields is None:
        update_fields = {}

    if activate is not None:
        update_fields["publicationDatetime"] = None
        if activate:
            update_fields["publicationDatetime"] = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    logger.info("Batch update of offers: start", extra={"updated_fields": update_fields})

    for chunk in get_chunks(query, chunk_size=settings.BATCH_UPDATE_OFFERS_CHUNK_SIZE):
        raw_offer_ids, raw_venue_ids = zip(*chunk)
        offer_ids = set(raw_offer_ids)
        venue_ids = set(raw_venue_ids)

        updated_offer_ids |= offer_ids
        found_venue_ids |= venue_ids

        query_to_update = db.session.query(models.Offer).filter(models.Offer.id.in_(offer_ids))
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.flush()

        if activate is not None:
            on_commit(
                partial(
                    logger.info,
                    "Offers has been activated" if activate else "Offers has been deactivated",
                    technical_message_id="offers.activated" if activate else "offers.deactivated",
                    extra={"offer_ids": offer_ids, "venue_ids": venue_ids},
                )
            )

        on_commit(
            partial(
                search.async_index_offer_ids,
                offer_ids,
                reason=IndexationReason.OFFER_BATCH_UPDATE,
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

    log_extra = {
        "updated_fields": update_fields,
        "nb_offers": len(updated_offer_ids),
        "nb_venues": len(found_venue_ids),
    }
    logger.info("Batch update of offers: end", extra=log_extra)

    return updated_offer_ids


def reindex_recently_published_offers() -> None:
    end = get_naive_utc_now()
    start = end - datetime.timedelta(hours=1)
    offer_query = offers_repository.get_offers_by_publication_datetime(start=start, end=end)
    offer_query = offers_repository.exclude_offers_from_inactive_venue_provider(offer_query)

    ids_to_reindex = []
    for (offer_id,) in offer_query.with_entities(offers_models.Offer.id).yield_per(1000):
        ids_to_reindex.append(offer_id)

    search.async_index_offer_ids(ids_to_reindex, reason=IndexationReason.OFFER_PUBLICATION)


def send_future_offer_reminders(booking_allowed_datetime: datetime.datetime | None = None) -> None:
    offers_query = offers_repository.get_offers_by_booking_allowed_datetime(
        booking_allowed_datetime=booking_allowed_datetime
    )
    for offer in offers_query:
        reminders_notifications.notify_users_offer_is_bookable(offer=offer)


def set_upper_timespan_of_inactive_headline_offers() -> None:
    inactive_headline_offers = offers_repository.get_inactive_headline_offers()
    for headline_offer in inactive_headline_offers:
        headline_offer.timespan = db_utils.make_timerange(headline_offer.timespan.lower, date_utils.get_naive_utc_now())
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
        reason=IndexationReason.OFFER_REINDEXATION,
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
        headline_offer = models.HeadlineOffer(
            offer=offer, venue=offer.venue, timespan=(date_utils.get_naive_utc_now(),)
        )
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
                reason=IndexationReason.OFFER_REINDEXATION,
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
        headline_offer.timespan = db_utils.make_timerange(headline_offer.timespan.lower, date_utils.get_naive_utc_now())
        on_commit(
            partial(
                search.async_index_offer_ids,
                {headline_offer.offerId},
                reason=IndexationReason.OFFER_REINDEXATION,
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
        date_in_two_days = date_utils.get_naive_utc_now() + datetime.timedelta(days=2)
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
    if booking_limit_datetime:
        validation.check_booking_limit_datetime(None, beginning_datetime, booking_limit_datetime)
        validation.check_offer_is_bookable_before_stock_booking_limit_datetime(
            offer, booking_limit_datetime=booking_limit_datetime
        )

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
        priceCategory=price_category,
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

    on_commit(
        partial(
            search.async_index_offer_ids,
            [offer.id],
            reason=IndexationReason.STOCK_CREATION,
        ),
    )

    # This log is used for analytics purposes.
    # If you need to make a 'breaking change' of this log, please contact the data team.
    # Otherwise, you will break some dashboards
    log_extra_data: dict[str, typing.Any] = {
        "offer_id": created_stock.offerId,
        "stock_id": created_stock.id,
        "provider_id": creating_provider.id if creating_provider else None,
        "price": str(created_stock.price),
    }
    logger.info("Successfully created stock", extra=log_extra_data, technical_message_id="stock.created")

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
        if booking_limit_datetime:
            validation.check_offer_is_bookable_before_stock_booking_limit_datetime(
                stock.offer,
                booking_limit_datetime,
            )
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

    validation.check_stock_is_updatable(stock, editing_provider, modifications_set=set(modifications.keys()))

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
            reason=IndexationReason.STOCK_UPDATE,
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


def upsert_offer_thing_stocks(offer: models.Offer, inputs: list[offers_schemas.ThingStockUpsertInput]) -> None:
    """
    Update all non-event stocks of an offer.

    - If a stock exists in the DB but not in `stock_inputs`, it is soft-deleted.
    - Otherwise, stocks are updated or created as needed.
    """
    if offer.isEvent:
        raise exceptions.OfferException({"global": "Offer is an event."})

    stock_inputs = list(inputs)

    existing_stocks = {stock.id: stock for stock in offer.activeStocks if not stock.offer.isEvent}

    stock_inputs_to_create = [stock_input for stock_input in stock_inputs if stock_input["id"] is None]
    stock_inputs_to_update = [stock_input for stock_input in stock_inputs if stock_input["id"] is not None]
    for stock_input in stock_inputs_to_update:
        if stock_input["id"] not in existing_stocks:
            raise exceptions.OfferException({"global": "Trying to update a non-existing stock."})
    stock_ids_to_delete = set(existing_stocks) - {stock_input["id"] for stock_input in stock_inputs_to_update}

    for stock_input in stock_inputs_to_create:
        create_stock(
            offer,
            activation_codes=stock_input["activation_codes"],
            activation_codes_expiration_datetime=stock_input["activation_codes_expiration_datetime"],
            booking_limit_datetime=stock_input["booking_limit_datetime"],
            price=stock_input["price"],
            quantity=stock_input["quantity"],
        )

    for stock_input in stock_inputs_to_update:
        assert stock_input["id"]
        stock_to_edit = existing_stocks[stock_input["id"]]
        edit_stock(
            stock_to_edit,
            booking_limit_datetime=stock_input["booking_limit_datetime"],
            price=stock_input["price"],
            quantity=stock_input["quantity"],
        )

    for stock_id in stock_ids_to_delete:
        stock_to_delete = existing_stocks[stock_id]
        delete_stock(stock_to_delete)


def handle_stocks_edition(edited_stocks: list[tuple[models.Stock, bool]]) -> None:
    for stock, is_beginning_datetime_updated in edited_stocks:
        if is_beginning_datetime_updated:
            handle_event_stock_beginning_datetime_update(stock)


def handle_event_stock_beginning_datetime_update(stock: models.Stock) -> None:
    bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
    _notify_pro_upon_stock_edit_for_event_offer(stock, bookings)
    _notify_beneficiaries_upon_stock_edit(stock, bookings)  # TODO: (tcoudray-pass, 16/04/2025) rename this function


def finalize_offer(
    offer: models.Offer,
    publication_datetime: datetime.datetime | None,
    booking_allowed_datetime: datetime.datetime | None,
) -> models.Offer:
    """
    :publication_datetime     : //!\\ must be a naive utc datetime
    :booking_allowed_datetime : //!\\ must be a naive utc datetime
    """
    offer.finalizationDatetime = get_naive_utc_now()

    if publication_datetime:
        publication_datetime = publication_datetime.replace(second=0, microsecond=0)
        validation.check_publication_date(publication_datetime)
        offer.publicationDatetime = publication_datetime

    offer.bookingAllowedDatetime = booking_allowed_datetime

    on_commit(partial(search.async_index_offer_ids, [offer.id], reason=IndexationReason.OFFER_PUBLICATION))
    on_commit(
        partial(
            logger.info,
            "Offer has been published",
            extra={"offer_id": offer.id, "venue_id": offer.venueId, "offer_status": offer.status},
            technical_message_id="offer.published",
        )
    )

    return offer


def publish_offer(
    offer: models.Offer,
    publication_datetime: datetime.datetime | None = None,
    booking_allowed_datetime: datetime.datetime | None = None,
) -> models.Offer:
    """
    :publication_datetime     : //!\\ must be a naive utc datetime
    :booking_allowed_datetime : //!\\ must be a naive utc datetime
    """
    finalization_date = get_naive_utc_now()

    if not offer.finalizationDatetime:
        offer.finalizationDatetime = finalization_date

    if publication_datetime:
        publication_datetime = publication_datetime.replace(second=0, microsecond=0)
        validation.check_publication_date(publication_datetime)

    offer.bookingAllowedDatetime = booking_allowed_datetime

    if ean := offer.ean:
        validation.check_other_offer_with_ean_does_not_exist(ean, offer.venue, offer.id)

    if publication_datetime is not None:  # i.e. pro user schedules the publication in the future
        offer.publicationDatetime = publication_datetime
    else:  # i.e. pro user publishes the offer right away
        offer.publicationDatetime = finalization_date

        on_commit(
            partial(
                search.async_index_offer_ids,
                [offer.id],
                reason=IndexationReason.OFFER_PUBLICATION,
            )
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
    offer.lastValidationDate = date_utils.get_naive_utc_now()
    offer.lastValidationType = OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None

    is_neither_pending_nor_rejected = offer.validation not in (
        models.OfferValidationStatus.REJECTED,
        models.OfferValidationStatus.PENDING,
    )

    if isinstance(offer, models.Offer):
        # * PENDING offer: keep publication datetime that will be used when
        # offer will be validated.
        # * REJECTED offer: won't be published, publication datetime can be
        # removed
        # * other validation status: nothing to do.
        if offer.validation == models.OfferValidationStatus.REJECTED:
            offer.publicationDatetime = None

        if offer.isThing and offer.activeStocks:  # public API may create offers without stocks
            offer.lastValidationPrice = offer.max_price
    else:
        offer.isActive = is_neither_pending_nor_rejected

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
    db.session.flush()

    # the algolia sync for the stock will happen within this function
    cancelled_bookings = bookings_api.cancel_bookings_from_stock_by_offerer(stock, author_id, user_connect_as)

    # This log is used for analytics purposes.
    # If you need to make a 'breaking change' of this log, please contact the data team.
    # Otherwise, you will break some dashboards
    on_commit(
        partial(
            logger.info,
            "Deleted stock and cancelled its bookings",
            extra={
                "stock": stock.id,
                "bookings": [b.id for b in cancelled_bookings],
                "author_id": author_id,
                "user_connect_as": bool(user_connect_as),
            },
            technical_message_id="stock.deleted",
        )
    )

    if cancelled_bookings:
        for booking in cancelled_bookings:
            transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email(booking)

        transactional_mails.send_booking_cancellation_confirmation_by_pro_email(cancelled_bookings)

        on_commit(
            partial(
                push_notification_job.send_cancel_booking_notification.delay,
                [booking.id for booking in cancelled_bookings],
            )
        )

    # do not keep stocks without any booking: they have never been used,
    # there is no need to keep useless rows inside the database.
    stock_has_bookings = db.session.query(
        db.session.query(bookings_models.Booking).filter(bookings_models.Booking.stockId == stock.id).exists()
    ).scalar()
    if not stock_has_bookings:
        db.session.delete(stock)

    on_commit(
        partial(
            search.async_index_offer_ids,
            [stock.offerId],
            reason=IndexationReason.STOCK_DELETION,
        )
    )


def delete_stock(stock: models.Stock, author_id: int | None = None, user_connect_as: bool | None = None) -> None:
    validation.check_stock_is_deletable(stock)
    _delete_stock(stock, author_id, user_connect_as)


def create_movie_poster(product: models.Product, provider: providers_models.Provider, image: bytes) -> None:
    """
    Create a product mediation of type poster for a cinema product (ie. a movie)
    """
    image_id = str(uuid.uuid4())
    mediation = models.ProductMediation(
        productId=product.id,
        lastProvider=provider,
        imageType=offers_models.ImageType.POSTER,
        uuid=image_id,
    )
    db.session.add(mediation)
    thumb_storage.create_thumb(
        product,
        image,
        storage_id_suffix_str="",
        keep_ratio=True,
        object_id=image_id,
    )
    db.session.flush()


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

    db.session.add(mediation)
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
            reason=IndexationReason.MEDIATION_CREATION,
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
                reason=IndexationReason.MEDIATION_DELETION,
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
    allocineId: int | None = None,
) -> bool:
    provided_identifiers_count = sum(1 for identifier in [ean, visa, allocineId] if identifier is not None)
    if provided_identifiers_count != 1 or not criterion_ids:
        logger.error("add_criteria_to_offers must be called with exactly one identifier and at least one criterion.")
        return False

    offer_ids_to_tag: set[int] = set()

    product_query = db.session.query(models.Product)
    # Check for EAN first, then allocineId (preferred over visa), and finally visa to identify the product.
    if ean:
        ean = ean.replace("-", "").replace(" ", "")
        product_query = product_query.filter(models.Product.ean == ean)
    elif allocineId:
        product_query = product_query.filter(models.Product.extraData.op("->")("allocineId") == str(allocineId))
    elif visa:
        product_query = product_query.filter(models.Product.extraData["visa"].astext == visa)

    product = product_query.one_or_none()

    if product:
        linked_offer_ids_query = db.session.query(models.Offer.id).filter(
            models.Offer.productId == product.id, models.Offer.isActive
        )
        offer_ids_to_tag.update(offer_id for (offer_id,) in linked_offer_ids_query.all())

    unlinked_offer_query = db.session.query(models.Offer.id).filter(
        models.Offer.productId.is_(None), models.Offer.isActive
    )

    if ean:
        unlinked_offer_query = unlinked_offer_query.filter(models.Offer.ean == ean)
        offer_ids_to_tag.update(offer_id for (offer_id,) in unlinked_offer_query.all())
    # The allocineId data exists only for products. We need to find offers that have the visa of this product.
    elif (allocineId and product and product.extraData and product.extraData.get("visa")) or visa:
        unlinked_offer_query = unlinked_offer_query.filter(models.Offer._extraData["visa"].astext == visa)
        offer_ids_to_tag.update(offer_id for (offer_id,) in unlinked_offer_query.all())

    if not offer_ids_to_tag:
        return False

    values: list[dict[str, int]] = []
    for criterion_id in criterion_ids:
        logger.info("Adding criterion %s to %d offers", criterion_id, len(offer_ids_to_tag))
        values += [{"offerId": offer_id, "criterionId": criterion_id} for offer_id in offer_ids_to_tag]

    if values:
        db.session.execute(
            insert(criteria_models.OfferCriterion)
            .values(values)
            .on_conflict_do_nothing(index_elements=["offerId", "criterionId"])
        )
        db.session.flush()

        on_commit(
            partial(
                search.async_index_offer_ids,
                offer_ids_to_tag,
                reason=IndexationReason.CRITERIA_LINK,
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

    offers = offers_query.options(sa_orm.selectinload(models.Offer.stocks).selectinload(models.Stock.bookings)).all()

    offer_updated_counts = offers_query.update(
        values={
            "validation": models.OfferValidationStatus.REJECTED,
            "lastValidationDate": date_utils.get_naive_utc_now(),
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
                reason=IndexationReason.PRODUCT_REJECTION,
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
        .options(sa_orm.joinedload(models.OfferValidationRule.subRules))
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
    start_time = start_of_day - datetime.timedelta(days=2)
    end_time = start_of_day
    if process_all_expired:
        start_time = datetime.datetime(2000, 1, 1)  # arbitrary old date

    page = 0
    limit = settings.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE
    while True:
        offer_ids = offers_repository.get_expired_offer_ids(start_time, end_time, offset=page * limit, limit=limit)
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
        pgcode = getattr(error.orig, "pgcode", None)
        if pgcode == UNIQUE_VIOLATION:
            raise exceptions.OfferAlreadyReportedError() from error
        if pgcode == CHECK_VIOLATION:
            raise exceptions.ReportMalformed() from error
        raise

    transactional_mails.send_email_reported_offer_by_user(user, offer, reason, custom_reason)


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


def create_or_update_product_mediations(product: models.Product, images: TiteliveImage | None) -> None:
    if not images or (not images.recto and not images.verso):
        return

    new_images_data = []
    try:
        if images.recto:
            image_bytes_recto = titelive.download_titelive_image(images.recto)
            new_images_data.append((models.ImageType.RECTO, image_bytes_recto))
        if images.verso:
            image_bytes_verso = titelive.download_titelive_image(images.verso)
            new_images_data.append((models.ImageType.VERSO, image_bytes_verso))

    except (
        requests.ExternalAPIException,
        PIL.UnidentifiedImageError,
        OSError,
        offers_exceptions.ImageValidationError,
    ) as err:
        logger.error(
            "Error downloading Titelive image for product %s",
            product.id,
            extra={"exception": err, "ean": product.ean},
        )
        return

    provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)

    with atomic():
        try:
            db.session.query(models.ProductMediation).filter(
                models.ProductMediation.productId == product.id,
                models.ProductMediation.lastProviderId == provider.id,
            ).delete(synchronize_session=False)

            for image_type, image_bytes in new_images_data:
                image_id = str(uuid.uuid4())
                mediation = models.ProductMediation(
                    productId=product.id,
                    lastProvider=provider,
                    imageType=image_type,
                    uuid=image_id,
                )
                db.session.add(mediation)
                db.session.flush()

                thumb_storage.create_thumb(
                    product,
                    image_bytes,
                    keep_ratio=True,
                    object_id=image_id,
                )
        except Exception as err:
            logger.error(
                "Error during product mediations update for product %s.",
                product.id,
                extra={"exception": err, "ean": product.ean},
            )
            mark_transaction_as_invalid()


def whitelist_product(idAtProviders: str, update_images: bool = False) -> models.Product:
    titelive_data = get_new_product_from_ean13(idAtProviders)

    product = fetch_or_update_product_with_titelive_data(titelive_data.product)

    product.gcuCompatibilityType = models.GcuCompatibilityType.COMPATIBLE

    db.session.add(product)
    db.session.flush()
    if update_images:
        create_or_update_product_mediations(product, titelive_data.images)
    return product


def revalidate_offers_after_product_whitelist(product: offers_models.Product, user: users_models.User) -> None:
    offers_query = db.session.query(offers_models.Offer).filter(
        offers_models.Offer.productId == product.id,
        offers_models.Offer.validation == offers_models.OfferValidationStatus.REJECTED,
        offers_models.Offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
    )
    offer_ids = [o.id for o in offers_query.with_entities(offers_models.Offer.id)]

    if offer_ids:
        offers_query.update(
            values={
                "validation": offers_models.OfferValidationStatus.APPROVED,
                "lastValidationDate": date_utils.get_naive_utc_now(),
                "lastValidationType": OfferValidationType.MANUAL,
                "lastValidationAuthorUserId": user.id,
            },
            synchronize_session=False,
        )
        db.session.flush()
        on_commit(
            partial(
                search.async_index_offer_ids,
                offer_ids,
                reason=IndexationReason.PRODUCT_WHITELIST_ADDITION,
                log_extra={"ean": product.ean},
            )
        )


def fetch_or_update_product_with_titelive_data(titelive_product: models.Product) -> models.Product:
    product = db.session.query(models.Product).filter_by(ean=titelive_product.ean).one_or_none()
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


def batch_delete_draft_offers(query: sa_orm.Query) -> None:
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
    db.session.add(created_price_category)
    db.session.flush()
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

    db.session.add(price_category)

    stocks_to_edit = [stock for stock in offer.stocks if stock.priceCategoryId == price_category.id]
    for stock in stocks_to_edit:
        edit_stock(stock, price=price_category.price, editing_provider=editing_provider)

    return price_category


def delete_price_category(offer: models.Offer, price_category: models.PriceCategory) -> None:
    """
    Deletes a price category and its related stocks, by cascade, if the offer is still in draft.
    The stock is truly deleted instead of being soft deleted.
    """
    validation.check_price_categories_deletable(offer, price_category)
    db.session.delete(price_category)
    db.session.flush()


def approves_provider_product_and_rejected_offers(ean: str) -> None:
    product = (
        db.session.query(models.Product)
        .filter(
            models.Product.gcuCompatibilityType == models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
            models.Product.ean == ean,
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
                    "lastValidationDate": date_utils.get_naive_utc_now(),
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
                reason=IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
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
    if data is None:
        raise exceptions.OfferHasNoStock()

    return StocksStats(*data)


def check_can_move_event_offer(offer: models.Offer) -> list[offerers_models.Venue]:
    if not offer.isEvent:
        raise exceptions.OfferIsNotEvent()

    count_past_stocks = (
        db.session.query(models.Stock)
        .with_entities(models.Stock.id)
        .filter(
            models.Stock.offerId == offer.id,
            models.Stock.beginningDatetime < date_utils.get_naive_utc_now(),
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
        .filter(
            models.Stock.offerId == offer.id,
            bookings_models.Booking.venueId == original_venue.id,
        )
        .limit(10_000)
    )
    bookings = db.session.query(bookings_models.Booking).filter(bookings_models.Booking.id.in_(bookings_ids))

    # After offer is moved, price categories must remain linked to labels defined for the related venue.
    # Extra SQL queries to avoid multiplying the number of rows in case of many labels
    db.session.flush()
    original_price_category_labels = {price_category.priceCategoryLabel for price_category in offer.priceCategories}
    labels_mapping = {
        price_category_label: _get_or_create_same_price_category_label(destination_venue, price_category_label)
        for price_category_label in original_price_category_labels
    }
    db.session.flush()
    with transaction():
        # Use a different OA if the offer uses the venue's OA
        if offer.offererAddress and offer.offererAddress == original_venue.offererAddress:
            destination_oa = offerers_api.get_or_create_offer_location(
                original_venue.managingOffererId, original_venue.offererAddress.addressId, original_venue.common_name
            )
            db.session.add(destination_oa)
            offer.offererAddress = destination_oa

        offer.venue = destination_venue
        db.session.add(offer)

        for price_category in offer.priceCategories:
            price_category.priceCategoryLabel = labels_mapping[price_category.priceCategoryLabel]
            db.session.add(price_category)

        while updated_bookings := bookings.update({"venueId": destination_venue.id}, synchronize_session=False):
            logger.info("Updated %d bookings for offer %d", updated_bookings, offer_id)

    on_commit(
        partial(
            search.async_index_offer_ids,
            {offer_id},
            reason=IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"venueId"}},
        )
    )


def move_event_offer(
    offer: models.Offer,
    destination_venue: offerers_models.Venue,
    *,
    move_offer_address: bool = False,
    notify_beneficiary: bool = False,
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
        if move_offer_address:
            offer.offererAddressId = destination_venue.offererAddressId
        else:
            # Use a different OA if the offer uses the venue OA
            if offer.offererAddress and offer.offererAddress == offer.venue.offererAddress:
                destination_oa = offerers_api.get_or_create_offer_location(
                    offer.venue.managingOffererId, offer.venue.offererAddress.addressId, offer.venue.common_name
                )
                db.session.add(destination_oa)
                offer.offererAddress = destination_oa
        offer.venue = destination_venue
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
            reason=IndexationReason.OFFER_UPDATE,
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
        stock.price = decimal.Decimal(str(new_price))
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


def _str_are_similar(str_1: str, str_2: str) -> bool:
    return (str_1 in str_2) or (str_2 in str_1) or (difflib.SequenceMatcher(None, str_1, str_2).ratio() >= 0.6)


def _should_merge_product(
    product_with_allocine_id: offers_models.Product,
    product_with_visa: offers_models.Product,
) -> bool:
    """
    Check that the 2 products are actually similar.

    Similarity checks are performed on their names, and, if defined, on their descriptions.
    """
    allocine_name = product_with_allocine_id.name.lower()
    visa_name = product_with_visa.name.lower()

    names_are_similar = _str_are_similar(visa_name, allocine_name)

    descriptions_are_similar = None
    if product_with_visa.description and product_with_allocine_id.description:
        allocine_description = product_with_allocine_id.description.lower()
        visa_description = product_with_visa.description.lower()

        descriptions_are_similar = _str_are_similar(visa_description, allocine_description)

    if descriptions_are_similar is not None:
        return names_are_similar and descriptions_are_similar

    return names_are_similar


def _select_matching_product(
    movie: offers_models.Movie,
    product_with_allocine_id: offers_models.Product,
    product_with_visa: offers_models.Product,
) -> offers_models.Product:
    """
    Return the most coherent product based on two comparisons :
        - on the movie title
        - on the movie description (if defined)
    """
    movie_name = movie.title.lower()
    allocine_name = product_with_allocine_id.name.lower()
    visa_name = product_with_visa.name.lower()

    similarity_ratio_to_allocine_product = difflib.SequenceMatcher(None, movie_name, allocine_name).ratio()
    similarity_ratio_to_visa_product = difflib.SequenceMatcher(None, movie_name, visa_name).ratio()

    if movie.description:
        movie_description = movie.description.lower()
        allocine_description = (product_with_allocine_id.description or "").lower()
        visa_description = (product_with_visa.description or "").lower()
        similarity_ratio_to_allocine_product = (
            similarity_ratio_to_allocine_product
            + difflib.SequenceMatcher(None, movie_description, allocine_description).ratio()
        ) / 2
        similarity_ratio_to_visa_product = (
            similarity_ratio_to_visa_product
            + difflib.SequenceMatcher(None, movie_description, visa_description).ratio()
        ) / 2

    if similarity_ratio_to_allocine_product < similarity_ratio_to_visa_product:
        return product_with_visa

    return product_with_allocine_id


def upsert_movie_product_from_provider(
    movie: offers_models.Movie, provider: providers_models.Provider
) -> offers_models.Product | None:
    if not movie.allocine_id and not movie.visa:
        logger.warning("Cannot create a movie product without allocineId nor visa")
        return None

    # (tcoudray-pass, 04/07/25) TODO: Move truncation outside this function
    if len(movie.title) > 140:
        movie.title = movie.title[0:139] + "…"

    products = offers_repository.get_movie_products_matching_allocine_id_or_film_visa(movie.allocine_id, movie.visa)

    # Case 1: Creation of a new a product
    if not products:
        with transaction():
            product = offers_models.Product(
                description=movie.description,
                durationMinutes=movie.duration,
                extraData=None,
                lastProviderId=provider.id,
                name=movie.title,
                subcategoryId=subcategories.SEANCE_CINE.id,
            )
            _update_product_extra_data(product, movie)
            db.session.add(product)
        return product

    # Case 2: Update of one existing product
    if len(products) == 1:
        product = products[0]
        if _is_allocine(provider.id) or provider.id == product.lastProviderId:
            with transaction():
                _update_movie_product(product, movie, provider.id)
        return product

    # Case 3: 2 products were returned
    if products[0].extraData and products[0].extraData.get("allocineId"):  # mypy does not know extraData cannot be None
        product_with_allocine_id, product_with_visa = products
    else:
        product_with_visa, product_with_allocine_id = products

    with transaction():
        if _should_merge_product(product_with_visa, product_with_allocine_id):
            # Case 3.1: the 2 products should be merged into one
            logger.info(
                "Merging movie products %d (to keep) and %d (to delete)",
                product_with_allocine_id.id,
                product_with_visa.id,
                extra={
                    "allocine_id": movie.allocine_id,
                    "visa": movie.visa,
                    "provider_id": provider.id,
                    "deleted": {
                        "name": product_with_visa.name,
                        "description": product_with_visa.description,
                    },
                    "kept": {
                        "name": product_with_allocine_id.name,
                        "description": product_with_allocine_id.description,
                    },
                },
            )
            product = offers_repository.merge_products(product_with_allocine_id, product_with_visa)
            if _is_allocine(provider.id) or provider.id == product.lastProviderId:
                _update_movie_product(product, movie, provider.id)
        else:
            # Case 3.2: the 2 products are DIFFERENT -> selection of the most coherent one
            # we do NOT update the product because if we reached this step, it means
            # the provider has sent us incoherent visa and allocineId
            product = _select_matching_product(movie, product_with_allocine_id, product_with_visa)
            logger.warning(
                "Provider sent incoherent visa and allocineId",
                extra={
                    "movie": {
                        "allocine_id": movie.allocine_id,
                        "visa": movie.visa,
                        "title": movie.title,
                        "description": movie.description,
                    },
                    "provider_id": provider.id,
                    "product_id": product.id,
                },
            )

    return product


def _is_allocine(provider_id: int) -> bool:
    allocine_products_provider_id = get_allocine_products_provider().id
    provider = get_provider_by_local_class("AllocineStocks")
    assert provider  # helps mypy
    allocine_stocks_provider_id = provider.id
    return provider_id in (allocine_products_provider_id, allocine_stocks_provider_id)


def _update_movie_product(product: offers_models.Product, movie: offers_models.Movie, provider_id: int) -> None:
    product.description = movie.description
    product.durationMinutes = movie.duration
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

    filtered_updates = {key: value for key, value in extra_data.items() if value is not None}
    product.extraData.update(typing.cast(offers_models.OfferExtraData, filtered_updates))


def delete_offers_stocks_related_objects(offer_ids: typing.Collection[int]) -> None:
    stock_ids_query = db.session.query(models.Stock.id).filter(models.Stock.offerId.in_(offer_ids))
    stock_ids = [row[0] for row in stock_ids_query]

    for chunk in get_chunks(stock_ids, chunk_size=128):
        db.session.query(models.ActivationCode).filter(
            models.ActivationCode.stockId.in_(chunk),
            # All bookingId should be None if venue_has_bookings is False,
            # keep condition to get an exception otherwise
            models.ActivationCode.bookingId.is_(None),
        ).delete(synchronize_session=False)


def _fix_price_categories(offer_ids: typing.Collection[int]) -> None:
    # In production database, we still have many price categories used in a stocks associated with different offers,
    # whereas by model, a PriceCategory should be used only in stocks for PriceCategory.offer.
    # So `ondelete="CASCADE"` set on PriceCategory.offerId makes offer deletion fail when not all these different offers
    # are deleted at the same time.
    # Instead of running a script which duplicates price categories to ensure that one is linked to stocks of a single
    # offer, the choice is made here to reassign price category to the Stock.offer which persists after running
    # delete_offers_and_all_related_objects, so that the PriceCategory is not deleted and there is no IntegrityError.
    stocks = (
        db.session.query(models.Stock)
        .join(models.Stock.priceCategory)
        .filter(
            models.Stock.offerId.not_in(offer_ids),
            models.PriceCategory.offerId.in_(offer_ids),
        )
        .options(
            sa_orm.load_only(models.Stock.offerId, models.Stock.priceCategoryId),
            sa_orm.contains_eager(models.Stock.priceCategory).load_only(models.PriceCategory.offerId),
        )
        .all()
    )

    if not stocks:
        return

    for stock in stocks:
        assert stock.priceCategory  # helps mypy
        stock.priceCategory.offerId = stock.offerId
        db.session.add(stock.priceCategory)

    db.session.flush()


def delete_offers_related_objects(offer_ids: typing.Collection[int]) -> None:
    delete_offers_stocks_related_objects(offer_ids)
    _fix_price_categories(offer_ids)

    related_models = [
        models.Stock,
        users_models.Favorite,
        models.Mediation,
        models.OfferReport,
        finance_models.CustomReimbursementRule,
    ]

    for model in related_models:
        db.session.query(model).filter(model.offerId.in_(offer_ids)).delete(synchronize_session=False)  # type: ignore[attr-defined]

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

        db.session.query(models.Offer).filter(models.Offer.id.in_(chunk)).delete(synchronize_session=False)
        db.session.flush()

        log_extra = {"round": idx, "offers_count": len(chunk), "time_spent": str(time.time() - start)}
        logger.info("delete offers and related objects: round %d, end", idx, extra=log_extra)

    redis_client = current_app.redis_client
    for idx, chunk in enumerate(get_chunks(offer_ids, chunk_size=offer_chunk_size)):
        try:
            with atomic():
                delete_offers_related_objects_round(idx, chunk)

            max_deleted_id = max(chunk)
            redis_client.set("DELETE_UNBOOKABLE_UNBOOKED_OLD_OFFERS_START_ID", max_deleted_id)
        except sa.exc.IntegrityError as err:
            extra = _format_db_error_extra(err, chunk)
            logger.error("delete_offers_and_all_related_objects: error", extra=extra)
            continue
        except Exception as err:
            extra = _format_error_extra(err, chunk)
            logger.error("delete_offers_and_all_related_objects: error", extra=extra)
            continue


def delete_unbookable_unbooked_old_offers(
    min_id: int | None = None,
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

    redis_client = current_app.redis_client
    max_offer_id = db.session.query(sa.func.max(models.Offer.id)).scalar()

    if min_id is None:
        min_id = redis_client.get("DELETE_UNBOOKABLE_UNBOOKED_OLD_OFFERS_START_ID")
        min_id = int(min_id) if min_id is not None else 0

    if max_id is None:
        # 10% of offers by run at most, no need to run for days
        max_id = min_id + (max_offer_id // 10)

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

    if max_id >= max_offer_id:
        # all offers have been scaned -> restart
        redis_client.set("DELETE_UNBOOKABLE_UNBOOKED_OLD_OFFERS_START_ID", 0)

    log_extra["time_spent"] = time.time() - start  # type: ignore[assignment]
    log_extra["deleted_offers_count"] = count
    logger.info("delete_unbookable_unbooked_unmodified_old_offers end", extra=log_extra)


def fetch_inconsistent_products(batch_size: int = 10_000) -> set[int]:
    def get_query_product_ids(query: sa.sql.expression.Select) -> list[int]:
        return [product_id for product_id, _ in db.session.execute(query)]

    product_max_id = db.session.execute(sa.select(sa.func.max(models.Product.id))).scalar()
    if not product_max_id:
        return set()

    product_ids = set()
    start = 0
    while start < product_max_id:
        end = start + batch_size
        batch_result = get_query_product_ids(_chronicles_count_query(start, end))
        batch_result += get_query_product_ids(_headlines_count_query(start, end))
        batch_result += get_query_product_ids(_likes_count_query(start, end))

        product_ids.update(batch_result)
        start += batch_size

    return product_ids


def update_product_counts(batch_size: int) -> None:
    _update_product_count("chroniclesCount", _chronicles_count_query, batch_size)
    _update_product_count("headlinesCount", _headlines_count_query, batch_size)
    _update_product_count("likesCount", _likes_count_query, batch_size)


def _update_product_count(
    column_name: str, query_fn: typing.Callable[[int, int], sa.sql.expression.Select], batch_size: int
) -> None:
    product_max_id = db.session.execute(sa.text("SELECT LAST_VALUE FROM product_id_seq")).scalar()
    if not product_max_id:
        return

    start = 0
    while start <= product_max_id:
        end = start + batch_size
        inconsistent_products_cte = query_fn(start, end).cte()
        update_statement = (
            sa.update(offers_models.Product)
            .values(
                {
                    column_name: sa.select(inconsistent_products_cte.c.count)
                    .where(inconsistent_products_cte.c.product_id == offers_models.Product.id)
                    .scalar_subquery()
                }
            )
            .where(offers_models.Product.id.in_(sa.select(inconsistent_products_cte.c.product_id)))
            .execution_options(synchronize_session=False)
        )
        with atomic():
            db.session.execute(update_statement)

        start += batch_size


def _chronicles_count_query(start: int, end: int) -> sa.sql.expression.Select:
    product_id = models.Product.id.label("product_id")
    count = sa.func.count(models.Product.id).label("count")
    return (
        sa.select(product_id, count)
        .select_from(chronicles_models.ProductChronicle)
        .join(models.Product, models.Product.id == chronicles_models.ProductChronicle.productId)
        .where(
            chronicles_models.ProductChronicle.productId >= start,
            chronicles_models.ProductChronicle.productId < end,
        )
        .group_by(models.Product.id, models.Product.chroniclesCount)
        .having(models.Product.chroniclesCount != count)
    )


def _headlines_count_query(start: int, end: int) -> sa.sql.expression.Select:
    product_id = models.Product.id.label("product_id")
    count = sa.func.count(models.Product.id).label("count")
    return (
        sa.select(product_id, count)
        .select_from(models.HeadlineOffer)
        .join(models.Offer, models.HeadlineOffer.offerId == models.Offer.id)
        .join(models.Product, models.Offer.productId == models.Product.id)
        .where(models.Offer.productId >= start, models.Offer.productId < end)
        .group_by(models.Product.id)
        .having(models.Product.headlinesCount != count)
    )


def _likes_count_query(start: int, end: int) -> sa.sql.expression.Select:
    product_id = models.Product.id.label("product_id")
    count = sa.func.count(models.Product.id).label("count")
    return (
        sa.select(product_id, count)
        .select_from(reactions_models.Reaction)
        .join(models.Product, reactions_models.Reaction.productId == models.Product.id)
        .where(
            reactions_models.Reaction.reactionType == reactions_models.ReactionTypeEnum.LIKE,
            reactions_models.Reaction.productId >= start,
            reactions_models.Reaction.productId < end,
        )
        .group_by(models.Product.id)
        .having(models.Product.likesCount != count)
    )


def upsert_highlight_requests(
    highlight_ids: list[int], offer: offers_models.Offer
) -> list[highlights_models.HighlightRequest]:
    """
    This method manages the highlight requests for a specific offer, based on a new, given list of highlight IDs. It ensures that the offer only has requests for the provided IDs while preserving historical data for statistics.
    - First, this method verifies the existence and availability of all the provided highlight IDs
    - Then, it deletes existing highlight requests for this offer that meet both of these conditions:
        - The highlight ID is not in the new list provided
        - The highlight is still available (not finished)
    - Note: Requests linked to highlights that are no longer available (finished) are retained for statistical purposes and are never deleted.
    - Finally, it creates new highlight requests only for the remaining provided IDs where a request does not already exist, preventing duplicates.
    """
    highlights = (
        db.session.query(highlights_models.Highlight).filter(highlights_models.Highlight.id.in_(highlight_ids)).all()
    )

    if len(highlights) < len(highlight_ids):
        raise exceptions.HighlightNotFoundException()

    if any(not h.is_available for h in highlights):
        raise exceptions.UnavailableHighlightException()

    today = datetime.date.today()
    current_highlight_requests = (
        db.session.query(highlights_models.HighlightRequest)
        .join(highlights_models.HighlightRequest.highlight)
        .filter(
            highlights_models.Highlight.availability_datespan.contains(today),
            highlights_models.HighlightRequest.offerId == offer.id,
        )
        .options(sa_orm.joinedload(highlights_models.HighlightRequest.highlight))
        .all()
    )

    current_highlight_ids = {highlight_request.highlight.id for highlight_request in current_highlight_requests}
    highlight_ids_to_delete = current_highlight_ids - set(highlight_ids)

    db.session.query(highlights_models.HighlightRequest).filter(
        highlights_models.HighlightRequest.highlightId.in_(highlight_ids_to_delete),
        highlights_models.HighlightRequest.offerId == offer.id,
    ).delete()

    if highlight_ids_to_delete:
        on_commit(
            partial(
                logger.info,
                "Highlight requests have been deleted",
                extra={
                    "offer_id": offer.id,
                    "venue_id": offer.venueId,
                    "highlight_ids": sorted(list(highlight_ids_to_delete)),
                },
                technical_message_id="offer.highlightRequests.deleted",
            )
        )

    highlight_requests = [
        highlight_request
        for highlight_request in current_highlight_requests
        if highlight_request.highlightId not in highlight_ids_to_delete
    ]

    highlight_ids_of_highlight_requests_to_create = set(highlight_ids) - current_highlight_ids
    for highlight_id in highlight_ids_of_highlight_requests_to_create:
        highlight_request = highlights_models.HighlightRequest(offerId=offer.id, highlightId=highlight_id)
        highlight_requests.append(highlight_request)
        db.session.add(highlight_request)

    if highlight_ids_of_highlight_requests_to_create:
        on_commit(
            partial(
                logger.info,
                "Highlight requests have been created",
                extra={
                    "offer_id": offer.id,
                    "venue_id": offer.venueId,
                    "highlight_ids": sorted(list(highlight_ids_of_highlight_requests_to_create)),
                },
                technical_message_id="offer.highlightRequests.created",
            )
        )
    try:
        db.session.flush()
    except sa_exc.IntegrityError:
        raise exceptions.HighlightRequestAlreadyExistsException()
    return highlight_requests
