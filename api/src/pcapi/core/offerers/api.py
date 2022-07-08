from datetime import datetime
import logging
import secrets
import typing
from typing import Optional

import sqlalchemy as sa

from pcapi import settings
import pcapi.connectors.thumb_storage as storage
from pcapi.core import search
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
import pcapi.core.finance.models as finance_models
from pcapi.core.mails.transactional.pro import new_offerer_validation
from pcapi.core.mails.transactional.pro import offerer_attachment_validation
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.users.external as users_external
import pcapi.core.users.models as users_models
import pcapi.core.users.repository as users_repository
from pcapi.domain import admin_emails
from pcapi.models import db
from pcapi.models import feature
from pcapi.repository import repository
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
import pcapi.routes.serialization.base as serialize_base
from pcapi.utils import crypto
from pcapi.utils import human_ids
from pcapi.utils import image_conversion
import pcapi.utils.db as db_utils

from . import exceptions
from . import models
from . import repository as offerers_repository
from . import validation


logger = logging.getLogger(__name__)

UNCHANGED = object()
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "postalCode", "city", "latitude", "longitude", "criteria"]
API_KEY_SEPARATOR = "_"


def create_digital_venue(offerer: models.Offerer) -> models.Venue:
    digital_venue = models.Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeCode = models.VenueTypeCode.DIGITAL  # type: ignore [attr-defined]
    digital_venue.managingOfferer = offerer
    digital_venue.dmsToken = generate_dms_token()
    return digital_venue


def update_venue(
    venue: models.Venue,
    contact_data: serialize_base.VenueContactModel = None,
    **attrs: typing.Any,
) -> models.Venue:
    validation.validate_coordinates(attrs.get("latitude"), attrs.get("longitude"))
    # FUTURE-NEW-BANK-DETAILS: clean up when new bank details journey is complete
    update_reimbursement_point_id = "reimbursementPointId" in attrs
    reimbursement_point_id = attrs.pop("reimbursementPointId", None)
    collectiveDomains = attrs.pop("collectiveDomains", None)
    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    validation.check_venue_edition(modifications, venue)

    if contact_data:
        upsert_venue_contact(venue, contact_data)

    if not modifications:
        return venue

    # FUTURE-NEW-BANK-DETAILS: clean up when new bank details journey is complete
    business_unit_id = modifications.get("businessUnitId")
    if business_unit_id and venue.isBusinessUnitMainVenue:
        delete_business_unit(venue.businessUnit)
        logger.info(
            "Change Venue.businessUnitId where Venue.siret and BusinessUnit.siret are equal",
            extra={"venue_id": venue.id, "business_unit_id": business_unit_id},
        )
    if "businessUnitId" in modifications:
        set_business_unit_to_venue_id(modifications["businessUnitId"], venue.id)

    if update_reimbursement_point_id:
        if feature.FeatureToggle.ENABLE_NEW_BANK_INFORMATIONS_CREATION.is_active():
            link_venue_to_reimbursement_point(venue, reimbursement_point_id)
        else:
            raise feature.DisabledFeatureError("This function is behind a deactivated feature flag.")

    old_booking_email = venue.bookingEmail if modifications.get("bookingEmail") else None

    if collectiveDomains:
        venue.collectiveDomains = educational_repository.get_educational_domains_from_ids(collectiveDomains)  # type: ignore [assignment]

    venue.populate_from_dict(modifications)

    repository.save(venue)
    search.async_index_venue_ids([venue.id])

    indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)
    if indexing_modifications_fields or contact_data:
        search.async_index_offers_of_venue_ids([venue.id])

    # Former booking email address shall no longer receive emails about data related to this venue.
    # If booking email was only in this object, this will clear all columns here and it will never be updated later.
    users_external.update_external_pro(old_booking_email)
    users_external.update_external_pro(venue.bookingEmail)

    return venue


def delete_business_unit(business_unit: finance_models.BusinessUnit) -> None:
    finance_models.BusinessUnitVenueLink.query.filter(
        finance_models.BusinessUnitVenueLink.businessUnit == business_unit,
        sa.func.upper(finance_models.BusinessUnitVenueLink.timespan).is_(None),
    ).update(
        {
            "timespan": sa.func.tsrange(
                sa.func.lower(finance_models.BusinessUnitVenueLink.timespan),
                datetime.utcnow(),
                "[)",
            )
        },
        synchronize_session=False,
    )
    models.Venue.query.filter(models.Venue.businessUnitId == business_unit.id).update(
        {"businessUnitId": None}, synchronize_session=False
    )

    business_unit.status = finance_models.BusinessUnitStatus.DELETED
    db.session.add(business_unit)
    db.session.commit()
    logger.info("Set BusinessUnit.status as DELETED", extra={"business_unit_id": business_unit.id})


def upsert_venue_contact(venue: models.Venue, contact_data: serialize_base.VenueContactModel) -> models.Venue:
    """
    Create and attach a VenueContact to a Venue if it has none.
    Update (replace) an existing VenueContact otherwise.
    """
    venue_contact = venue.contact
    if not venue_contact:
        venue_contact = models.VenueContact(venue=venue)

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


def create_venue(venue_data: venues_serialize.PostVenueBodyModel) -> models.Venue:
    data = venue_data.dict(by_alias=True)
    validation.check_venue_creation(data)
    venue = models.Venue()
    venue.populate_from_dict(data)

    if venue_data.contact:
        upsert_venue_contact(venue, venue_data.contact)
    venue.dmsToken = generate_dms_token()
    repository.save(venue)

    if venue_data.businessUnitId:
        set_business_unit_to_venue_id(venue_data.businessUnitId, venue.id)

    search.async_index_venue_ids([venue.id])

    users_external.update_external_pro(venue.bookingEmail)

    return venue


# TODO(fseguin, 2022-06-26, FUTURE-NEW-BANK-DETAILS): remove when new bank details journey is complete
def set_business_unit_to_venue_id(
    business_unit_id: Optional[int],
    venue_id: int,
    timestamp: Optional[datetime] = None,
) -> None:
    if not timestamp:
        timestamp = datetime.utcnow()
    current_link = finance_models.BusinessUnitVenueLink.query.filter(
        finance_models.BusinessUnitVenueLink.venueId == venue_id,
        finance_models.BusinessUnitVenueLink.timespan.contains(timestamp),
    ).one_or_none()
    if current_link:
        current_link.timespan = db_utils.make_timerange(
            current_link.timespan.lower,
            timestamp,
        )
        db.session.add(current_link)
    if business_unit_id:
        new_link = finance_models.BusinessUnitVenueLink(
            businessUnitId=business_unit_id, venueId=venue_id, timespan=(timestamp, None)
        )
        db.session.add(new_link)
    models.Venue.query.filter(models.Venue.id == venue_id).update({"businessUnitId": business_unit_id})
    db.session.commit()


def link_venue_to_pricing_point(
    venue: models.Venue,
    pricing_point_id: int,
    timestamp: Optional[datetime] = None,
    force_link: bool = False,
) -> None:
    """
    Creates a VenuePricingPointLink if the venue had not been previously linked to a pricing point.
    If it had, then it will raise an error, unless the force_link parameter is True, in exceptional circumstances.
    """
    if not feature.FeatureToggle.ENABLE_NEW_BANK_INFORMATIONS_CREATION.is_active():
        raise feature.DisabledFeatureError("This function is behind a deactivated feature flag.")
    validation.check_venue_can_be_linked_to_pricing_point(venue, pricing_point_id)
    if not timestamp:
        timestamp = datetime.utcnow()
    current_link = models.VenuePricingPointLink.query.filter(
        models.VenuePricingPointLink.venueId == venue.id,
        models.VenuePricingPointLink.timespan.contains(timestamp),
    ).one_or_none()
    if current_link:
        if force_link:
            current_link.timespan = db_utils.make_timerange(
                current_link.timespan.lower,
                timestamp,
            )
            db.session.add(current_link)
        else:
            raise exceptions.CannotLinkVenueToPricingPoint(
                f"This Venue is already linked to Venue #{current_link.pricingPointId} for pricing"
            )
    new_link = models.VenuePricingPointLink(
        pricingPointId=pricing_point_id, venueId=venue.id, timespan=(timestamp, None)
    )
    db.session.add(new_link)
    db.session.commit()
    if current_link and force_link:
        logger.info(
            "Venue was previously linked to another Venue for pricing, and has been linked to a new pricing point",
            extra={
                "venue_id": venue.id,
                "previous_pricing_point_id": current_link.pricingPointId,
                "new_pricing_point_id": pricing_point_id,
            },
        )


def link_venue_to_reimbursement_point(
    venue: models.Venue,
    reimbursement_point_id: Optional[int],
    timestamp: Optional[datetime] = None,
) -> None:
    if not feature.FeatureToggle.ENABLE_NEW_BANK_INFORMATIONS_CREATION.is_active():
        raise feature.DisabledFeatureError("This function is behind a deactivated feature flag.")
    if reimbursement_point_id:
        validation.check_venue_can_be_linked_to_reimbursement_point(venue, reimbursement_point_id)
    if not timestamp:
        timestamp = datetime.utcnow()
    current_link = models.VenueReimbursementPointLink.query.filter(
        models.VenueReimbursementPointLink.venueId == venue.id,
        models.VenueReimbursementPointLink.timespan.contains(timestamp),
    ).one_or_none()
    if current_link:
        current_link.timespan = db_utils.make_timerange(
            current_link.timespan.lower,
            timestamp,
        )
        db.session.add(current_link)
    if reimbursement_point_id:
        new_link = models.VenueReimbursementPointLink(
            reimbursementPointId=reimbursement_point_id, venueId=venue.id, timespan=(timestamp, None)
        )
        db.session.add(new_link)
    db.session.commit()


def generate_and_save_api_key(offerer_id: int) -> str:
    if models.ApiKey.query.filter_by(offererId=offerer_id).count() >= settings.MAX_API_KEY_PER_OFFERER:
        raise exceptions.ApiKeyCountMaxReached()
    model_api_key, clear_api_key = generate_api_key(offerer_id)
    repository.save(model_api_key)
    return clear_api_key


def generate_api_key(offerer_id: int) -> tuple[models.ApiKey, str]:
    clear_secret = secrets.token_hex(32)
    prefix = _generate_api_key_prefix()
    key = models.ApiKey(offererId=offerer_id, prefix=prefix, secret=crypto.hash_password(clear_secret))

    return key, f"{prefix}{API_KEY_SEPARATOR}{clear_secret}"


def _generate_api_key_prefix() -> str:
    for _ in range(100):
        prefix_identifier = secrets.token_hex(6)
        prefix = _create_prefix(settings.ENV, prefix_identifier)
        if not db.session.query(models.ApiKey.query.filter_by(prefix=prefix).exists()).scalar():
            return prefix
    raise exceptions.ApiKeyPrefixGenerationError()


def find_api_key(key: str) -> Optional[models.ApiKey]:
    try:
        env, prefix_identifier, clear_secret = key.split(API_KEY_SEPARATOR)
        prefix = _create_prefix(env, prefix_identifier)
    except ValueError:
        # TODO: remove this legacy behaviour once we forbid old keys
        return models.ApiKey.query.filter_by(value=key).one_or_none()

    api_key = models.ApiKey.query.filter_by(prefix=prefix).one_or_none()

    if not api_key:
        return None

    return api_key if api_key.check_secret(clear_secret) else None


def _create_prefix(env: str, prefix_identifier: str) -> str:
    return f"{env}{API_KEY_SEPARATOR}{prefix_identifier}"


def delete_api_key_by_user(user: users_models.User, api_key_prefix: str) -> None:
    api_key = models.ApiKey.query.filter_by(prefix=api_key_prefix).one()

    if not user.has_access(api_key.offererId):
        raise exceptions.ApiKeyDeletionDenied()

    db.session.delete(api_key)


def create_offerer(user: users_models.User, offerer_informations: offerers_serialize.CreateOffererQueryModel):  # type: ignore [no-untyped-def]
    offerer = offerers_repository.find_offerer_by_siren(offerer_informations.siren)

    if offerer is not None:
        user_offerer = grant_user_offerer_access(offerer, user)
        user_offerer.generate_validation_token()
        repository.save(user_offerer)

    else:
        offerer = models.Offerer()
        offerer.address = offerer_informations.address
        offerer.city = offerer_informations.city
        offerer.name = offerer_informations.name
        offerer.postalCode = offerer_informations.postalCode
        offerer.siren = offerer_informations.siren
        offerer.generate_validation_token()
        digital_venue = create_digital_venue(offerer)
        user_offerer = grant_user_offerer_access(offerer, user)
        repository.save(offerer, digital_venue, user_offerer)

    if not admin_emails.maybe_send_offerer_validation_email(offerer, user_offerer):
        logger.warning(
            "Could not send validation email to offerer",
            extra={"user_offerer": user_offerer.id},
        )

    users_external.update_external_pro(user.email)

    return user_offerer


def grant_user_offerer_access(offerer: models.Offerer, user: users_models.User) -> models.UserOfferer:
    return models.UserOfferer(offerer=offerer, user=user)


def validate_offerer_attachment(token: str) -> None:
    user_offerer = offerers_repository.find_user_offerer_by_validation_token(token)
    if user_offerer is None:
        raise exceptions.ValidationTokenNotFoundError()

    user_offerer.validationToken = None
    user_offerer.user.add_pro_role()
    repository.save(user_offerer)

    users_external.update_external_pro(user_offerer.user.email)

    if not offerer_attachment_validation.send_offerer_attachment_validation_email_to_pro(user_offerer):
        logger.warning(
            "Could not send attachment validation email to offerer",
            extra={"user_offerer": user_offerer.id},
        )


def validate_offerer(token: str) -> None:
    offerer = offerers_repository.find_offerer_by_validation_token(token)
    if offerer is None:
        raise exceptions.ValidationTokenNotFoundError()

    applicants = users_repository.get_users_with_validated_attachment_by_offerer(offerer)
    offerer.validationToken = None
    offerer.dateValidated = datetime.utcnow()
    for applicant in applicants:
        applicant.add_pro_role()
    managed_venues = offerer.managedVenues

    repository.save(offerer, *applicants)
    search.async_index_offers_of_venue_ids([venue.id for venue in managed_venues])

    for applicant in applicants:
        users_external.update_external_pro(applicant.email)

    if not new_offerer_validation.send_new_offerer_validation_email_to_pro(offerer):
        logger.warning(
            "Could not send validation confirmation email to offerer",
            extra={"offerer": offerer.id},
        )


def get_timestamp_from_url(image_url: str) -> str:
    return int(image_url.split("_")[-1])  # type: ignore [return-value]


def rm_previous_venue_thumbs(venue: models.Venue) -> None:
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
    user: users_models.User,
    venue: models.Venue,
    content: bytes,
    image_credit: str,
    crop_params: Optional[image_conversion.CropParams] = None,
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
        ratio=image_conversion.ImageRatio.LANDSCAPE,
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


def delete_venue_banner(venue: models.Venue) -> None:
    rm_previous_venue_thumbs(venue)
    repository.save(venue)
    search.async_index_venue_ids([venue.id])


def can_offerer_create_educational_offer(offerer_id: Optional[int]) -> None:
    import pcapi.core.educational.adage_backends as adage_client

    if offerer_id is None:
        return

    if offerers_repository.offerer_has_venue_with_adage_id(offerer_id):
        return

    siren = offerers_repository.find_siren_by_offerer_id(offerer_id)
    try:
        response = adage_client.get_adage_offerer(siren)
        if len(response) == 0:
            raise educational_exceptions.CulturalPartnerNotFoundException(
                "No venue has been found for the selected siren"
            )
    except (
        educational_exceptions.CulturalPartnerNotFoundException,
        educational_exceptions.AdageException,
    ) as exception:
        raise exception


def get_educational_offerers(offerer_id: Optional[str], current_user: users_models.User) -> list[models.Offerer]:
    if current_user.has_admin_role and offerer_id is None:
        logger.info("Admin user must provide offerer_id as a query parameter")
        raise exceptions.MissingOffererIdQueryParameter

    if offerer_id and current_user.has_admin_role:
        offerers = models.Offerer.query.filter(
            models.Offerer.isValidated,
            models.Offerer.isActive.is_(True),
            models.Offerer.id == human_ids.dehumanize(offerer_id),
        ).all()

    else:
        offerers = (
            offerers_repository.get_all_offerers_for_user(
                user=current_user,
                validated=True,
            )
            .distinct(models.Offerer.id)
            .all()
        )
    return offerers


def get_eligible_for_search_venues(
    max_venues: typing.Optional[int] = None,
) -> typing.Generator[models.Venue, None, None]:
    query = models.Venue.query.options(
        # needed by is_eligible_for_search
        sa.orm.joinedload(models.Venue.managingOfferer).load_only(
            models.Offerer.isActive,
        )
    )

    if max_venues:
        query = query.limit(max_venues)

    for venue in query.yield_per(1_000):
        if venue.is_eligible_for_search:
            yield venue


def get_offerer_by_collective_offer_id(collective_offer_id: int) -> models.Offerer:
    return offerers_repository.get_by_collective_offer_id(collective_offer_id)


def get_offerer_by_collective_offer_template_id(collective_offer_id: int) -> models.Offerer:
    return offerers_repository.get_by_collective_offer_template_id(collective_offer_id)


def has_venue_at_least_one_bookable_offer(venue: models.Venue) -> bool:
    if not feature.FeatureToggle.ENABLE_VENUE_STRICT_SEARCH.is_active():
        return True

    if not venue.is_eligible_for_search or not venue.isReleased:
        return False

    at_least_one_eligible_offer_query = (
        offers_models.Stock.query.join(offers_models.Offer)
        .filter(offers_models.Offer.venueId == venue.id)
        .filter(offers_models.Offer.is_eligible_for_search)
        .exists()
    )

    return db.session.query(at_least_one_eligible_offer_query).scalar()


def generate_dms_token() -> str:
    """
    Returns a 12-char hex str of 6 random bytes
    The collision probability is 0.001 for 750k Venues
    """
    for _i in range(10):
        dms_token = secrets.token_hex(6)
        if not offerers_repository.dms_token_exists(dms_token):
            return dms_token
    raise ValueError("Could not generate new dmsToken for Venue")


def get_venues_educational_statuses() -> list[offerers_models.VenueEducationalStatus]:
    return offerers_repository.get_venues_educational_statuses()
