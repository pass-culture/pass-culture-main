from datetime import datetime
import logging
import secrets
import typing
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors import thumb_storage as storage
from pcapi.connectors.api_adage import AdageException
from pcapi.connectors.api_adage import CulturalPartnerNotFoundException
from pcapi.core import search
import pcapi.core.finance.models as finance_models
from pcapi.core.mails.transactional.pro.new_offerer_validation import send_new_offerer_validation_email_to_pro
from pcapi.core.mails.transactional.pro.offerer_attachment_validation import (
    send_offerer_attachment_validation_email_to_pro,
)
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.exceptions import MissingOffererIdQueryParameter
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueContact
from pcapi.core.offerers.repository import find_offerer_by_siren
from pcapi.core.offerers.repository import find_offerer_by_validation_token
from pcapi.core.offerers.repository import find_siren_by_offerer_id
from pcapi.core.offerers.repository import find_user_offerer_by_validation_token
from pcapi.core.offerers.repository import get_all_offerers_for_user
from pcapi.core.offerers.repository import get_by_collective_offer_id
from pcapi.core.offerers.repository import get_by_collective_offer_template_id
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.models import User
from pcapi.core.users.repository import get_users_with_validated_attachment_by_offerer
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.models import db
from pcapi.repository import repository
from pcapi.routes.serialization import base as serialize_base
from pcapi.routes.serialization.offerers_serialize import CreateOffererQueryModel
from pcapi.routes.serialization.venues_serialize import PostVenueBodyModel
from pcapi.utils import crypto
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio

from . import validation
from .exceptions import ApiKeyCountMaxReached
from .exceptions import ApiKeyDeletionDenied
from .exceptions import ApiKeyPrefixGenerationError
from .exceptions import ValidationTokenNotFoundError


logger = logging.getLogger(__name__)

UNCHANGED = object()
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "postalCode", "city", "latitude", "longitude", "criteria"]
API_KEY_SEPARATOR = "_"


def create_digital_venue(offerer: Offerer) -> Venue:
    digital_venue = Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeCode = offerers_models.VenueTypeCode.DIGITAL  # type: ignore [attr-defined]
    digital_venue.managingOfferer = offerer
    return digital_venue


def update_venue(
    venue: Venue,
    contact_data: serialize_base.VenueContactModel = None,
    **attrs: typing.Any,
) -> Venue:
    validation.validate_coordinates(attrs.get("latitude"), attrs.get("longitude"))
    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    validation.check_venue_edition(modifications, venue)

    if contact_data:
        upsert_venue_contact(venue, contact_data)

    if not modifications:
        return venue

    business_unit_id = modifications.get("businessUnitId")
    if business_unit_id and venue.businessUnit:
        if venue.businessUnitId != business_unit_id and venue.isBusinessUnitMainVenue:
            delete_business_unit(venue.businessUnit)
            logger.info(
                "Change Venue.businessUnitId where Venue.siret and BusinessUnit.siret are equal",
                extra={"venue_id": venue.id, "business_unit_id": business_unit_id},
            )

    old_booking_email = venue.bookingEmail if modifications.get("bookingEmail") else None

    venue.populate_from_dict(modifications)

    repository.save(venue)
    search.async_index_venue_ids([venue.id])

    indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)
    if indexing_modifications_fields or contact_data:
        search.async_index_offers_of_venue_ids([venue.id])

    # Former booking email address shall no longer receive emails about data related to this venue.
    # If booking email was only in this object, this will clear all columns here and it will never be updated later.
    update_external_pro(old_booking_email)
    update_external_pro(venue.bookingEmail)

    return venue


def delete_business_unit(business_unit: finance_models.BusinessUnit) -> None:
    finance_models.BusinessUnitVenueLink.query.update(
        {
            "timespan": sa.func.tsrange(
                sa.func.lower(finance_models.BusinessUnitVenueLink.timespan),
                datetime.utcnow(),
                "[)",
            )
        },
        synchronize_session=False,
    )
    Venue.query.filter(Venue.businessUnitId == business_unit.id).update(
        {"businessUnitId": None}, synchronize_session=False
    )

    business_unit.status = finance_models.BusinessUnitStatus.DELETED
    db.session.add(business_unit)
    db.session.commit()
    logger.info("Set BusinessUnit.status as DELETED", extra={"business_unit_id": business_unit.id})


def upsert_venue_contact(venue: Venue, contact_data: serialize_base.VenueContactModel) -> Venue:
    """
    Create and attach a VenueContact to a Venue if it has none.
    Update (replace) an existing VenueContact otherwise.
    """
    venue_contact = venue.contact
    if not venue_contact:
        venue_contact = VenueContact(venue=venue)

    modifications = {
        field: value
        for field, value in contact_data.dict().items()
        if venue_contact.field_exists_and_has_changed(field, value)
    }
    if not modifications:
        return venue

    venue_contact.email = contact_data.email
    venue_contact.website = contact_data.website
    venue_contact.phone_number = contact_data.phone_number
    venue_contact.social_medias = contact_data.social_medias or {}

    repository.save(venue_contact)
    return venue


def create_venue(venue_data: PostVenueBodyModel) -> Venue:
    data = venue_data.dict(by_alias=True)
    validation.check_venue_creation(data)
    venue = Venue()
    venue.populate_from_dict(data)

    if venue_data.contact:
        upsert_venue_contact(venue, venue_data.contact)

    repository.save(venue)

    search.async_index_venue_ids([venue.id])

    update_external_pro(venue.bookingEmail)

    return venue


def set_business_unit_to_venue_id(business_unit_id: int, venue_id: int) -> None:
    now = datetime.utcnow()
    current_link = finance_models.BusinessUnitVenueLink.query.filter(
        finance_models.BusinessUnitVenueLink.venueId == venue_id,
        finance_models.BusinessUnitVenueLink.timespan.contains(now),
    ).one_or_none()
    if current_link:
        current_link.timespan = current_link._make_timespan(
            current_link.timespan.lower,
            now,
        )
        db.session.add(current_link)
    new_link = finance_models.BusinessUnitVenueLink(
        businessUnitId=business_unit_id, venueId=venue_id, timespan=(now, None)
    )
    db.session.add(new_link)
    Venue.query.filter(Venue.id == venue_id).update({"businessUnitId": business_unit_id})
    db.session.commit()


def generate_and_save_api_key(offerer_id: int) -> str:
    if ApiKey.query.filter_by(offererId=offerer_id).count() >= settings.MAX_API_KEY_PER_OFFERER:
        raise ApiKeyCountMaxReached()
    model_api_key, clear_api_key = generate_api_key(offerer_id)
    repository.save(model_api_key)
    return clear_api_key


def generate_api_key(offerer_id: int) -> tuple[ApiKey, str]:
    clear_secret = secrets.token_hex(32)
    prefix = _generate_api_key_prefix()
    key = ApiKey(offererId=offerer_id, prefix=prefix, secret=crypto.hash_password(clear_secret))

    return key, f"{prefix}{API_KEY_SEPARATOR}{clear_secret}"


def _generate_api_key_prefix() -> str:
    for _ in range(100):
        prefix_identifier = secrets.token_hex(6)
        prefix = _create_prefix(settings.ENV, prefix_identifier)
        if not db.session.query(ApiKey.query.filter_by(prefix=prefix).exists()).scalar():
            return prefix
    raise ApiKeyPrefixGenerationError()


def find_api_key(key: str) -> Optional[ApiKey]:
    try:
        env, prefix_identifier, clear_secret = key.split(API_KEY_SEPARATOR)
        prefix = _create_prefix(env, prefix_identifier)
    except ValueError:
        # TODO: remove this legacy behaviour once we forbid old keys
        return ApiKey.query.filter_by(value=key).one_or_none()

    api_key = ApiKey.query.filter_by(prefix=prefix).one_or_none()

    if not api_key:
        return None

    return api_key if api_key.check_secret(clear_secret) else None


def _create_prefix(env: str, prefix_identifier: str) -> str:
    return f"{env}{API_KEY_SEPARATOR}{prefix_identifier}"


def delete_api_key_by_user(user: User, api_key_prefix: str) -> None:
    api_key = ApiKey.query.filter_by(prefix=api_key_prefix).one()

    if not user.has_access(api_key.offererId):
        raise ApiKeyDeletionDenied()

    db.session.delete(api_key)


def create_offerer(user: User, offerer_informations: CreateOffererQueryModel):  # type: ignore [no-untyped-def]
    offerer = find_offerer_by_siren(offerer_informations.siren)

    if offerer is not None:
        user_offerer = grant_user_offerer_access(offerer, user)
        user_offerer.generate_validation_token()
        repository.save(user_offerer)

    else:
        offerer = Offerer()
        offerer.address = offerer_informations.address
        offerer.city = offerer_informations.city
        offerer.name = offerer_informations.name
        offerer.postalCode = offerer_informations.postalCode
        offerer.siren = offerer_informations.siren
        offerer.generate_validation_token()
        digital_venue = create_digital_venue(offerer)
        user_offerer = grant_user_offerer_access(offerer, user)
        repository.save(offerer, digital_venue, user_offerer)

    _send_to_pc_admin_offerer_to_validate_email(offerer, user_offerer)

    update_external_pro(user.email)

    return user_offerer


def grant_user_offerer_access(offerer: Offerer, user: User) -> UserOfferer:
    return UserOfferer(offerer=offerer, user=user)


def _send_to_pc_admin_offerer_to_validate_email(offerer: Offerer, user_offerer: UserOfferer) -> None:
    if not maybe_send_offerer_validation_email(offerer, user_offerer):
        logger.warning(
            "Could not send validation email to offerer",
            extra={"user_offerer": user_offerer.id},
        )


def validate_offerer_attachment(token: str) -> None:
    user_offerer = find_user_offerer_by_validation_token(token)
    if user_offerer is None:
        raise ValidationTokenNotFoundError()

    user_offerer.validationToken = None
    user_offerer.user.add_pro_role()
    repository.save(user_offerer)

    update_external_pro(user_offerer.user.email)

    if not send_offerer_attachment_validation_email_to_pro(user_offerer):
        logger.warning(
            "Could not send attachment validation email to offerer",
            extra={"user_offerer": user_offerer.id},
        )


def validate_offerer(token: str) -> None:
    offerer = find_offerer_by_validation_token(token)
    if offerer is None:
        raise ValidationTokenNotFoundError()

    applicants = get_users_with_validated_attachment_by_offerer(offerer)
    offerer.validationToken = None
    offerer.dateValidated = datetime.utcnow()
    for applicant in applicants:
        applicant.add_pro_role()
    managed_venues = offerer.managedVenues

    repository.save(offerer, *applicants)
    search.async_index_offers_of_venue_ids([venue.id for venue in managed_venues])

    for applicant in applicants:
        update_external_pro(applicant.email)

    if not send_new_offerer_validation_email_to_pro(offerer):
        logger.warning(
            "Could not send validation confirmation email to offerer",
            extra={"offerer": offerer.id},
        )


def get_timestamp_from_url(image_url: str) -> str:
    return int(image_url.split("_")[-1])  # type: ignore [return-value]


def rm_previous_venue_thumbs(venue: Venue) -> None:
    if not venue.bannerUrl:
        return

    # handle old banner urls that did not have a timestamp
    timestamp = get_timestamp_from_url(venue.bannerUrl) if "_" in venue.bannerUrl else 0
    storage.remove_thumb(venue, image_index=timestamp)  # type: ignore [arg-type]

    # some older venues might have a banner but not the original file
    # note: if bannerUrl is not None, bannerMeta should not be either.
    if original_image_url := venue.bannerMeta.get("original_image_url"):  # type: ignore [union-attr]
        original_image_timestamp = get_timestamp_from_url(original_image_url)
        storage.remove_thumb(venue, image_index=original_image_timestamp)  # type: ignore [arg-type]

    venue.bannerUrl = None
    venue.bannerMeta = None


def save_venue_banner(
    user: User,
    venue: Venue,
    content: bytes,
    image_credit: str,
    crop_params: Optional[CropParams] = None,
) -> None:
    """
    Save the new venue's new banner: crop it and resize it if asked
    or needed, and save the original image too (shrinked if too big,
    but with the same ratio).

    The previous banner (if any) is removed.

    Use a timestamps as indexes in order to have a unique URL for each
    upload.
    """
    rm_previous_venue_thumbs(venue)

    banner_timestamp = int(datetime.utcnow().timestamp())
    storage.create_thumb(
        model_with_thumb=venue,
        image_as_bytes=content,
        image_index=banner_timestamp,
        crop_params=crop_params,
        ratio=ImageRatio.LANDSCAPE,
    )

    original_image_timestamp = banner_timestamp + 1
    storage.create_thumb(
        model_with_thumb=venue, image_as_bytes=content, image_index=original_image_timestamp, keep_ratio=True
    )

    venue.bannerUrl = f"{venue.thumbUrl}_{banner_timestamp}"
    venue.bannerMeta = {
        "image_credit": image_credit,
        "author_id": user.id,
        "original_image_url": f"{venue.thumbUrl}_{original_image_timestamp}",
        "crop_params": crop_params,
    }

    repository.save(venue)

    search.async_index_venue_ids([venue.id])


def delete_venue_banner(venue: Venue) -> None:
    rm_previous_venue_thumbs(venue)
    repository.save(venue)
    search.async_index_venue_ids([venue.id])


def can_offerer_create_educational_offer(offerer_id: Optional[int]) -> None:
    import pcapi.core.educational.adage_backends as adage_client

    if not offerer_id:
        return

    siren = find_siren_by_offerer_id(offerer_id)
    try:
        response = adage_client.get_adage_offerer(siren)
        if len(response) == 0:
            raise CulturalPartnerNotFoundException("No venue has been found for the selected siren")
    except (CulturalPartnerNotFoundException, AdageException) as exception:
        raise exception


def get_educational_offerers(offerer_id: Optional[str], current_user: User) -> list[Offerer]:
    if current_user.has_admin_role and offerer_id is None:
        logger.info("Admin user must provide offerer_id as a query parameter")
        raise MissingOffererIdQueryParameter

    if offerer_id and current_user.has_admin_role:
        offerers = Offerer.query.filter(
            Offerer.validationToken.is_(None), Offerer.isActive.is_(True), Offerer.id == dehumanize(offerer_id)
        ).all()

    else:
        offerers = (
            get_all_offerers_for_user(
                user=current_user,
                validated=True,
                validated_for_user=True,
            )
            .distinct(Offerer.id)
            .all()
        )
    return offerers


def get_eligible_for_search_venues(max_venues: typing.Optional[int] = None) -> typing.Generator[Venue, None, None]:
    query = Venue.query.options(
        # needed by is_eligible_for_search
        sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
            offerers_models.Offerer.isActive,
        )
    )

    if max_venues:
        query = query.limit(max_venues)

    for venue in query.yield_per(1_000):
        if venue.is_eligible_for_search:
            yield venue


def get_offerer_by_collective_offer_id(collective_offer_id: int) -> Offerer:
    return get_by_collective_offer_id(collective_offer_id)


def get_offerer_by_collective_offer_template_id(collective_offer_id: int) -> Offerer:
    return get_by_collective_offer_template_id(collective_offer_id)
