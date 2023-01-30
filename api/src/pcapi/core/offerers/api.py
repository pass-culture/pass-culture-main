from datetime import date
from datetime import datetime
import enum
import logging
import secrets
import time
import typing

from flask_sqlalchemy import BaseQuery
import jwt
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors import sirene
import pcapi.connectors.thumb_storage as storage
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.external import zendesk_sell
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.finance.models as finance_models
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
import pcapi.core.users.repository as users_repository
from pcapi.domain import admin_emails
from pcapi.models import db
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import repository
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
import pcapi.routes.serialization.base as serialize_base
from pcapi.utils import crypto
from pcapi.utils import human_ids
from pcapi.utils import image_conversion
from pcapi.utils.clean_accents import clean_accents
import pcapi.utils.db as db_utils
import pcapi.utils.email as email_utils
from pcapi.utils.regions import get_department_codes_for_region

from . import exceptions
from . import models
from . import repository as offerers_repository
from . import validation


logger = logging.getLogger(__name__)


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "postalCode", "city", "latitude", "longitude", "criteria"]
API_KEY_SEPARATOR = "_"
APE_TAG_MAPPING = {"84.11Z": "Collectivité"}


def create_digital_venue(offerer: models.Offerer) -> models.Venue:
    digital_venue = models.Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeCode = models.VenueTypeCode.DIGITAL
    digital_venue.managingOfferer = offerer
    digital_venue.dmsToken = generate_dms_token()
    return digital_venue


def update_venue(
    venue: models.Venue,
    contact_data: serialize_base.VenueContactModel = None,
    admin_update: bool = False,
    **attrs: typing.Any,
) -> models.Venue:
    validation.validate_coordinates(attrs.get("latitude"), attrs.get("longitude"))  # type: ignore [arg-type]
    reimbursement_point_id = attrs.pop("reimbursementPointId", None)

    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    if not admin_update:
        # run validation when the venue update is triggered by a pro
        # user. This can be bypassed when done by and admin/backoffice
        # user.
        validation.check_venue_edition(modifications, venue)

    if contact_data:
        upsert_venue_contact(venue, contact_data)

    if not modifications:
        return venue

    if reimbursement_point_id != venue.current_reimbursement_point_id:
        link_venue_to_reimbursement_point(venue, reimbursement_point_id)

    old_booking_email = venue.bookingEmail if modifications.get("bookingEmail") else None

    venue.populate_from_dict(modifications)

    repository.save(venue)
    search.async_index_venue_ids([venue.id])

    indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)
    if indexing_modifications_fields or contact_data:
        search.async_index_offers_of_venue_ids([venue.id])

    # Former booking email address shall no longer receive emails about data related to this venue.
    # If booking email was only in this object, this will clear all columns here and it will never be updated later.
    external_attributes_api.update_external_pro(old_booking_email)
    external_attributes_api.update_external_pro(venue.bookingEmail)
    zendesk_sell.update_venue(venue)

    return venue


def update_venue_collective_data(
    venue: models.Venue,
    **attrs: typing.Any,
) -> models.Venue:
    collective_domains_in_attrs = "collectiveDomains" in attrs
    collective_legal_status_in_attrs = "collectiveLegalStatus" in attrs
    collectiveDomains = attrs.pop("collectiveDomains", None)
    collectiveLegalStatus = attrs.pop("collectiveLegalStatus", None)

    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    if collective_domains_in_attrs:
        venue.collectiveDomains = educational_repository.get_educational_domains_from_ids(collectiveDomains or [])

    if collective_legal_status_in_attrs:
        if collectiveLegalStatus:
            venue.venueEducationalStatusId = collectiveLegalStatus
        else:
            venue.venueEducationalStatusId = None

    venue.populate_from_dict(modifications)

    repository.save(venue)

    zendesk_sell.update_venue(venue)

    return venue


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
    venue.populate_from_dict(data, skipped_keys=("contact",))

    if venue_data.contact:
        upsert_venue_contact(venue, venue_data.contact)
    venue.dmsToken = generate_dms_token()
    repository.save(venue)

    if venue.siret:
        link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

    search.async_index_venue_ids([venue.id])

    external_attributes_api.update_external_pro(venue.bookingEmail)
    zendesk_sell.create_venue(venue)

    return venue


def link_venue_to_pricing_point(
    venue: models.Venue,
    pricing_point_id: int,
    timestamp: datetime | None = None,
    force_link: bool = False,
) -> None:
    """
    Creates a VenuePricingPointLink if the venue had not been previously linked to a pricing point.
    If it had, then it will raise an error, unless the force_link parameter is True, in exceptional circumstances.
    """
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
    reimbursement_point_id: int | None,
    timestamp: datetime | None = None,
) -> None:
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
    # This is a soft limit for visual purposes only (not for security
    # reasons). A user could create more than MAX_API_KEY_PER_OFFERER
    # keys through a race condition. It's fine.
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


def find_api_key(key: str) -> models.ApiKey | None:
    if key.count(API_KEY_SEPARATOR) != 2:
        # Handle legacy keys that did not have any prefix. They were
        # plain 64-characters strings. They have been migrated so that
        # their prefix is their first 8 characters (and the rest is
        # their secret).
        env = settings.ENV
        prefix_identifier, clear_secret = key[:8], key[8:]
    else:
        env, prefix_identifier, clear_secret = key.split(API_KEY_SEPARATOR)
    prefix = _create_prefix(env, prefix_identifier)

    api_key = (
        models.ApiKey.query.filter_by(prefix=prefix)
        .options(
            sa_orm.joinedload(models.ApiKey.offerer),
        )
        .one_or_none()
    )

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


def _fill_in_offerer(
    offerer: offerers_models.Offerer, offerer_informations: offerers_serialize.CreateOffererQueryModel
) -> None:
    offerer.address = offerer_informations.address
    offerer.city = offerer_informations.city
    offerer.name = offerer_informations.name
    offerer.postalCode = offerer_informations.postalCode
    offerer.siren = offerer_informations.siren
    offerer.validationStatus = ValidationStatus.NEW
    offerer.dateCreated = datetime.utcnow()


def auto_tag_new_offerer(
    offerer: offerers_models.Offerer, siren_info: sirene.SirenInfo | None, user: users_models.User
) -> None:
    if siren_info:
        tag_label = APE_TAG_MAPPING.get(siren_info.ape_code)
        if tag_label:
            tag = offerers_models.OffererTag.query.filter_by(label=tag_label).one_or_none()
            if not tag:
                logger.error(
                    "Could not assign tag to offerer: tag not found in DB",
                    extra={"offerer": offerer.id, "tag_label": tag_label},
                )
            else:
                offerer.tags.append(tag)

    if (user.email).split("@")[-1] in set(settings.NATIONAL_PARTNERS_EMAIL_DOMAINS.split(",")):
        tag_name = "partenaire-national"
        tag = offerers_models.OffererTag.query.filter_by(name=tag_name).one_or_none()
        if not tag:
            logger.error(
                "Could not assign tag to offerer: tag not found in DB",
                extra={"offerer": offerer.id, "tag_name": tag_name},
            )
        else:
            offerer.tags.append(tag)
    db.session.add(offerer)
    db.session.commit()


def create_offerer(
    user: users_models.User, offerer_informations: offerers_serialize.CreateOffererQueryModel
) -> models.UserOfferer:
    offerer = offerers_repository.find_offerer_by_siren(offerer_informations.siren)
    is_new = False

    if offerer is not None:
        user_offerer = grant_user_offerer_access(offerer, user)
        objects_to_save = [user_offerer]
        if offerer.isRejected:
            # When offerer was rejected, it is considered as a new offerer in validation process;
            # history is kept with same id and siren
            is_new = True
            _fill_in_offerer(offerer, offerer_informations)
            comment = "Nouvelle demande sur un SIREN précédemment rejeté"
            objects_to_save += [offerer]
        else:
            user_offerer.validationStatus = ValidationStatus.NEW
            objects_to_save += [
                history_api.log_action(
                    history_models.ActionType.USER_OFFERER_NEW, user, user=user, offerer=offerer, save=False
                ),
            ]
        repository.save(*objects_to_save)

    else:
        is_new = True
        offerer = models.Offerer()
        _fill_in_offerer(offerer, offerer_informations)
        digital_venue = create_digital_venue(offerer)
        user_offerer = grant_user_offerer_access(offerer, user)
        comment = None
        repository.save(offerer, digital_venue, user_offerer)

    assert offerer.siren  # helps mypy until Offerer.siren is set as NOT NULL
    try:
        siren_info = sirene.get_siren(offerer.siren)
    except sirene.SireneException as exc:
        logger.info("Could not fetch info from Sirene API", extra={"exc": exc})
        siren_info = None

    if is_new:
        auto_tag_new_offerer(offerer, siren_info, user)

        extra_data = {}
        if siren_info:
            extra_data = {"sirene_info": dict(siren_info)}

        history_api.log_action(
            history_models.ActionType.OFFERER_NEW,
            user,
            user=user,
            offerer=offerer,
            comment=comment,
            **extra_data,  # type: ignore [arg-type]
        )

    if not admin_emails.maybe_send_offerer_validation_email(offerer, user_offerer, siren_info):
        logger.warning(
            "Could not send validation email to offerer",
            extra={"user_offerer": user_offerer.id},
        )

    external_attributes_api.update_external_pro(user.email)
    zendesk_sell.create_offerer(offerer)

    return user_offerer


def grant_user_offerer_access(offerer: models.Offerer, user: users_models.User) -> models.UserOfferer:
    return models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.VALIDATED)


def _format_tags(tags: typing.Iterable[models.OffererTag]) -> str:
    return ", ".join(sorted(tag.label for tag in tags))


def update_offerer(
    offerer: models.Offerer,
    city: str | T_UNCHANGED = UNCHANGED,
    postal_code: str | T_UNCHANGED = UNCHANGED,
    address: str | T_UNCHANGED = UNCHANGED,
    tags: list[models.OffererTag] | T_UNCHANGED = UNCHANGED,
) -> dict[str, dict[str, str | None]]:
    modified_info: dict[str, dict[str, str | None]] = {}

    if city is not UNCHANGED and offerer.city != city:
        modified_info["city"] = {"old_info": offerer.city, "new_info": city}
        offerer.city = city
    if postal_code is not UNCHANGED and offerer.postalCode != postal_code:
        modified_info["postalCode"] = {"old_info": offerer.postalCode, "new_info": postal_code}
        offerer.postalCode = postal_code
    if address is not UNCHANGED and offerer.address != address:
        modified_info["address"] = {"old_info": offerer.address, "new_info": address}
        offerer.address = address
    if tags is not UNCHANGED:
        if set(offerer.tags) != set(tags):
            modified_info["tags"] = {"old_info": _format_tags(offerer.tags), "new_info": _format_tags(tags)}
            offerer.tags = tags

    repository.save(offerer)

    zendesk_sell.update_offerer(offerer)

    return modified_info


def validate_offerer_attachment(
    user_offerer: offerers_models.UserOfferer, author_user: users_models.User, comment: str | None = None
) -> None:
    if user_offerer.isValidated:
        raise exceptions.UserOffererAlreadyValidatedException()

    user_offerer.user.add_pro_role()
    user_offerer.validationStatus = ValidationStatus.VALIDATED

    action = history_api.log_action(
        history_models.ActionType.USER_OFFERER_VALIDATED,
        author=author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
        save=False,
    )

    repository.save(user_offerer, action)

    external_attributes_api.update_external_pro(user_offerer.user.email)

    if not transactional_mails.send_offerer_attachment_validation_email_to_pro(user_offerer):
        logger.warning(
            "Could not send attachment validation email to offerer",
            extra={"user_offerer": user_offerer.id},
        )


def set_offerer_attachment_pending(
    user_offerer: offerers_models.UserOfferer, author_user: users_models.User, comment: str | None = None
) -> None:
    user_offerer.validationStatus = ValidationStatus.PENDING
    action = history_api.log_action(
        history_models.ActionType.USER_OFFERER_PENDING,
        author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
        save=False,
    )
    repository.save(user_offerer, action)


def reject_offerer_attachment(
    user_offerer: offerers_models.UserOfferer, author_user: users_models.User, comment: str | None = None
) -> None:
    db.session.add(
        history_api.log_action(
            history_models.ActionType.USER_OFFERER_REJECTED,
            author_user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment=comment,
            save=False,
        )
    )

    if not transactional_mails.send_offerer_attachment_rejection_email_to_pro(user_offerer):
        logger.warning(
            "Could not send rejection confirmation email to offerer",
            extra={"offerer": user_offerer.offerer.id},
        )

    db.session.delete(user_offerer)
    db.session.commit()


def validate_offerer(offerer: models.Offerer, author_user: users_models.User) -> None:
    if offerer.isValidated:
        raise exceptions.OffererAlreadyValidatedException()

    applicants = users_repository.get_users_with_validated_attachment_by_offerer(offerer)
    offerer.validationStatus = ValidationStatus.VALIDATED
    offerer.dateValidated = datetime.utcnow()
    for applicant in applicants:
        applicant.add_pro_role()
    managed_venues = offerer.managedVenues

    action = history_api.log_action(
        history_models.ActionType.OFFERER_VALIDATED,
        author_user,
        offerer=offerer,
        user=applicants[0] if applicants else None,  # before validation we should have only one applicant
        save=False,
    )

    repository.save(offerer, action, *applicants)
    search.async_index_offers_of_venue_ids([venue.id for venue in managed_venues])

    for applicant in applicants:
        external_attributes_api.update_external_pro(applicant.email)

    zendesk_sell.update_offerer(offerer)

    if applicants:
        if not transactional_mails.send_new_offerer_validation_email_to_pro(offerer):
            logger.warning(
                "Could not send validation confirmation email to offerer",
                extra={"offerer": offerer.id},
            )


def reject_offerer(
    offerer: offerers_models.Offerer, author_user: users_models.User, comment: str | None = None
) -> None:
    if offerer.isRejected:
        raise exceptions.OffererAlreadyRejectedException()

    applicants = users_repository.get_users_with_validated_attachment(offerer)
    first_user_to_register_offerer = applicants[0] if applicants else None

    was_validated = offerer.isValidated
    offerer.validationStatus = ValidationStatus.REJECTED
    offerer.dateValidated = None
    db.session.add(offerer)
    db.session.add(
        history_api.log_action(
            history_models.ActionType.OFFERER_REJECTED,
            author_user,
            offerer=offerer,
            user=first_user_to_register_offerer,
            comment=comment,
            save=False,
        )
    )

    if applicants:
        if not transactional_mails.send_new_offerer_rejection_email_to_pro(offerer):
            logger.warning(
                "Could not send rejection confirmation email to offerer",
                extra={"offerer": offerer.id},
            )

    # Detach user from offerer after sending transactional email to applicant
    models.UserOfferer.query.filter_by(offererId=offerer.id).delete()

    # Remove any API key which could have been created when user was waiting for validation
    models.ApiKey.query.filter(models.ApiKey.offererId == offerer.id).delete()

    db.session.commit()

    if was_validated:
        for applicant in applicants:
            external_attributes_api.update_external_pro(applicant.email)


def set_offerer_pending(
    offerer: offerers_models.Offerer, author_user: users_models.User, comment: str | None = None
) -> None:
    offerer.validationStatus = ValidationStatus.PENDING
    action = history_api.log_action(
        history_models.ActionType.OFFERER_PENDING, author_user, offerer=offerer, comment=comment, save=False
    )
    repository.save(offerer, action)


def add_comment_to_offerer(offerer: offerers_models.Offerer, author_user: users_models.User, comment: str) -> None:
    history_api.log_action(history_models.ActionType.COMMENT, author_user, offerer=offerer, comment=comment)


def add_comment_to_venue(venue: offerers_models.Venue, author_user: users_models.User, comment: str) -> None:
    history_api.log_action(history_models.ActionType.COMMENT, author_user, venue=venue, comment=comment)


def add_comment_to_offerer_attachment(
    user_offerer: offerers_models.UserOfferer, author_user: users_models.User, comment: str
) -> None:
    history_api.log_action(
        history_models.ActionType.COMMENT,
        author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )


def get_timestamp_from_url(image_url: str) -> str:
    return image_url.split("_")[-1]


def rm_previous_venue_thumbs(venue: models.Venue) -> None:
    if not venue.bannerUrl:
        return

    # handle old banner urls that did not have a timestamp
    timestamp = get_timestamp_from_url(venue.bannerUrl) if "_" in venue.bannerUrl else ""
    storage.remove_thumb(venue, storage_id_suffix=str(timestamp), ignore_thumb_count=True)

    # some older venues might have a banner but not the original file
    # note: if bannerUrl is not None, bannerMeta should not be either.
    assert venue.bannerMeta is not None
    if original_image_url := venue.bannerMeta.get("original_image_url"):
        original_image_timestamp = get_timestamp_from_url(original_image_url)
        storage.remove_thumb(venue, storage_id_suffix=original_image_timestamp)

    venue.bannerUrl = None
    venue.bannerMeta = None
    venue.thumbCount = 1


def save_venue_banner(
    user: users_models.User,
    venue: models.Venue,
    content: bytes,
    image_credit: str,
    crop_params: image_conversion.CropParams | None = None,
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

    updated_at = datetime.utcnow()
    banner_timestamp = str(int(updated_at.timestamp()))
    storage.create_thumb(
        model_with_thumb=venue,
        image_as_bytes=content,
        storage_id_suffix_str=banner_timestamp,
        crop_params=crop_params,
        ratio=image_conversion.ImageRatio.LANDSCAPE,
    )

    original_image_timestamp = str(int(updated_at.timestamp() + 1))
    storage.create_thumb(
        model_with_thumb=venue, image_as_bytes=content, storage_id_suffix_str=original_image_timestamp, keep_ratio=True
    )

    venue.bannerUrl = f"{venue.thumbUrl}_{banner_timestamp}"
    venue.bannerMeta = {
        "image_credit": image_credit,
        "author_id": user.id,
        "original_image_url": f"{venue.thumbUrl}_{original_image_timestamp}",
        "crop_params": crop_params,
        "updated_at": updated_at,
    }

    repository.save(venue)

    search.async_index_venue_ids([venue.id])


def delete_venue_banner(venue: models.Venue) -> None:
    rm_previous_venue_thumbs(venue)
    repository.save(venue)
    search.async_index_venue_ids([venue.id])


def can_offerer_create_educational_offer(offerer_id: int | None) -> None:
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


def get_educational_offerers(offerer_id: str | None, current_user: users_models.User) -> list[models.Offerer]:
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
    max_venues: int | None = None,
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


def get_venue_by_id(venue_id: int) -> offerers_models.Venue:
    return offerers_repository.get_venue_by_id(venue_id)


def search_offerer(search_query: str, order_by: list[str] | None = None) -> BaseQuery:
    offerers = models.Offerer.query

    search_query = search_query.strip()
    if not search_query:
        return offerers.filter(False)

    if search_query.isnumeric():
        if len(search_query) == 9:
            offerers = offerers.filter(
                sa.or_(models.Offerer.id == int(search_query), models.Offerer.siren == search_query)
            )
        else:
            offerers = offerers.filter(models.Offerer.id == int(search_query))
    else:
        offerers = offerers.filter(
            sa.func.similarity(models.Offerer.name, search_query) > settings.BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE
        )
        # Always order by similarity when searching by name
        offerers = offerers.order_by(sa.desc(sa.func.similarity(models.Offerer.name, search_query)))

    if order_by:
        try:
            offerers = offerers.order_by(*db_utils.get_ordering_clauses(models.Offerer, order_by))
        except db_utils.BadSortError as err:
            raise ApiErrors({"sorting": str(err)})

    # At the end, search by id, in case there is no order requested or equal similarity score
    else:
        offerers = offerers.order_by(models.Offerer.id)

    return offerers


def get_offerer_base_query(offerer_id: int) -> BaseQuery:
    return models.Offerer.query.filter(models.Offerer.id == offerer_id)


def search_venue(search_query: str, order_by: list[str] | None = None) -> BaseQuery:
    venues = models.Venue.query.outerjoin(offerers_models.VenueContact)
    terms = search_query.split()

    filters: list[sa.sql.ColumnElement] = []
    name_terms: list[str] = []

    if not terms:
        return venues.filter(False)

    for term in terms:
        if not term:
            continue

        term_filters: list[sa.sql.ColumnElement] = []

        # numeric
        if term.isnumeric():
            term_filters.append(models.Venue.id == int(term))
            if len(term) == 14:
                term_filters.append(models.Venue.siret == term)

        # email
        sanitized_term = email_utils.sanitize_email(term)
        if email_utils.is_valid_email(sanitized_term):
            term_filters.append(models.Venue.bookingEmail == sanitized_term)
            term_filters.append(models.VenueContact.email == sanitized_term)
        elif email_utils.is_valid_email_domain(sanitized_term):
            # search for all emails @domain.ext
            term_filters.append(models.Venue.bookingEmail.like(f"%{sanitized_term}"))
            term_filters.append(models.VenueContact.email.like(f"%{sanitized_term}"))

        if term_filters:
            filters.append(sa.or_(*term_filters) if len(term_filters) > 1 else term_filters[0])
        else:
            # non-numeric terms are searched by trigram distance in the name
            name_terms.append(term)

    name_search = " ".join(name_terms)
    if name_search:
        filters.append(
            sa.or_(
                sa.func.similarity(models.Venue.name, name_search)
                > settings.BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE,
                sa.func.similarity(models.Venue.publicName, name_search)
                > settings.BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE,
            )
        )

    # each result must match all terms in any column
    venues = venues.filter(*filters)

    if order_by:
        try:
            venues = venues.order_by(*db_utils.get_ordering_clauses(models.Venue, order_by))
        except db_utils.BadSortError as err:
            raise ApiErrors({"sorting": str(err)})

    if name_search:
        venues = venues.order_by(
            sa.desc(
                sa.func.similarity(models.Venue.name, name_search)
                + sa.func.similarity(models.Venue.publicName, name_search)
            )
        )

    # At the end, search by id, in case there is no order requested or equal similarity score
    if not order_by:
        venues = venues.order_by(models.Venue.id)

    return venues


def get_venue_base_query(venue_id: int) -> BaseQuery:
    return models.Venue.query.outerjoin(offerers_models.VenueContact).filter(models.Venue.id == venue_id)


def get_offerer_basic_info(offerer_id: int) -> sa.engine.Row:
    bank_informations_query = sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
        sa.select(
            sa.case(
                (
                    offerers_models.VenueReimbursementPointLink.id.is_(None)
                    | ~offerers_models.VenueReimbursementPointLink.timespan.contains(datetime.utcnow()),
                    "ko",
                ),
                else_="ok",
            ).label("status"),
            sa.func.count(offerers_models.Venue.id).label("number"),
        )
        .select_from(offerers_models.Venue)
        .outerjoin(
            offerers_models.VenueReimbursementPointLink,
            offerers_models.VenueReimbursementPointLink.venueId == offerers_models.Venue.id,
        )
        .filter(
            offerers_models.Venue.managingOffererId == offerer_id,
        )
        .group_by(sa.text("status"))
        .subquery()
    )
    is_collective_eligible_query = (
        sa.select(offerers_models.Venue)
        .filter(
            offerers_models.Venue.managingOffererId == offerer_id,
            sa.not_(offerers_models.Venue.venueEducationalStatusId.is_(None)),
        )
        .exists()
    )
    offerer_query = sa.select(
        offerers_models.Offerer.id,
        offerers_models.Offerer.name,
        offerers_models.Offerer.validationStatus,
        offerers_models.Offerer.isActive,
        offerers_models.Offerer.siren,
        offerers_models.Offerer.postalCode,
        bank_informations_query.scalar_subquery().label("bank_informations"),
        is_collective_eligible_query.label("is_collective_eligible"),
    ).filter(offerers_models.Offerer.id == offerer_id)

    offerer = db.session.execute(offerer_query).one_or_none()

    return offerer


def get_offerer_total_revenue(offerer_id: int) -> float:
    individual_revenue_query = sa.select(
        sa.func.coalesce(
            sa.func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity),
            0.0,
        )
    ).filter(
        bookings_models.Booking.offererId == offerer_id,
        bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED.value,
    )
    collective_revenue_query = (
        sa.select(
            sa.func.coalesce(
                sa.func.sum(educational_models.CollectiveStock.price),
                0.0,
            )
        )
        .select_from(
            educational_models.CollectiveBooking,
        )
        .join(
            educational_models.CollectiveStock,
            onclause=educational_models.CollectiveStock.id == educational_models.CollectiveBooking.collectiveStockId,
        )
        .filter(
            educational_models.CollectiveBooking.offererId == offerer_id,
            educational_models.CollectiveBooking.status != bookings_models.BookingStatus.CANCELLED.value,
        )
    )

    total_revenue_query = sa.select(
        individual_revenue_query.scalar_subquery() + collective_revenue_query.scalar_subquery()
    )

    return db.session.execute(total_revenue_query).scalar() or 0.0


def get_offerer_offers_stats(offerer_id: int) -> sa.engine.Row:
    individual_offers_query = sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
        sa.select(
            sa.case(
                [
                    (offers_models.Offer.isActive.is_(True), "active"),
                    (offers_models.Offer.isActive.is_(False), "inactive"),
                ]
            ).label("status"),
            sa.func.count(offers_models.Offer.id).label("number"),
        )
        .select_from(offerers_models.Venue)
        .outerjoin(offers_models.Offer)
        .filter(
            offerers_models.Venue.managingOffererId == offerer_id,
            offers_models.Offer.validation == offers_models.OfferValidationStatus.APPROVED.value,
        )
        .group_by(offers_models.Offer.isActive)
        .subquery()
    )
    collective_offers_query = sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
        sa.select(
            sa.case(
                [
                    (educational_models.CollectiveOffer.isActive.is_(True), "active"),
                    (educational_models.CollectiveOffer.isActive.is_(False), "inactive"),
                ]
            ).label("status"),
            sa.func.count(educational_models.CollectiveOffer.id).label("number"),
        )
        .select_from(offerers_models.Venue)
        .outerjoin(educational_models.CollectiveOffer)
        .filter(
            offerers_models.Venue.managingOffererId == offerer_id,
            educational_models.CollectiveOffer.validation == offers_models.OfferValidationStatus.APPROVED.value,
        )
        .group_by(educational_models.CollectiveOffer.isActive)
        .subquery()
    )

    offers_stats_query = sa.select(
        individual_offers_query.scalar_subquery().label("individual_offers"),
        collective_offers_query.label("collective_offers"),
    )

    return db.session.execute(offers_stats_query).one()


def get_venue_basic_info(venue_id: int) -> sa.engine.Row:
    dms_application_id_query = sa.select(finance_models.BankInformation.applicationId).filter(
        finance_models.BankInformation.venueId == venue_id
    )
    has_reimbursement_point_query = sa.select(sa.func.count(offerers_models.VenueReimbursementPointLink.id)).filter(
        offerers_models.VenueReimbursementPointLink.venueId == venue_id,
        offerers_models.VenueReimbursementPointLink.timespan.contains(datetime.utcnow()),
    )
    venue_query = (
        sa.select(
            offerers_models.Venue.id,
            offerers_models.Venue.common_name.label("name"),  # type: ignore[attr-defined]
            offerers_models.Venue.siret,
            sa.func.coalesce(
                offerers_models.VenueContact.email,
                offerers_models.Venue.bookingEmail,
            ).label("email"),
            offerers_models.VenueContact.phone_number,
            offerers_models.Venue.postalCode,
            offerers_models.Venue.dmsToken,
            offerers_models.Venue.venueEducationalStatusId,
            dms_application_id_query.scalar_subquery().label("dms_application_id"),
            has_reimbursement_point_query.scalar_subquery().label("has_reimbursement_point"),
        )
        .outerjoin(
            offerers_models.VenueContact,
        )
        .filter(
            offerers_models.Venue.id == venue_id,
        )
    )

    venue = db.session.execute(venue_query).one_or_none()

    return venue


def get_venue_total_revenue(venue_id: int) -> float:
    individual_revenue_query = sa.select(
        sa.func.coalesce(
            sa.func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity),
            0.0,
        )
    ).filter(
        bookings_models.Booking.venueId == venue_id,
        bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED.value,
    )
    collective_revenue_query = (
        sa.select(
            sa.func.coalesce(
                sa.func.sum(educational_models.CollectiveStock.price),
                0.0,
            )
        )
        .select_from(educational_models.CollectiveBooking)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .filter(
            educational_models.CollectiveBooking.venueId == venue_id,
            educational_models.CollectiveBooking.status != bookings_models.BookingStatus.CANCELLED.value,
        )
    )

    total_revenue_query = sa.select(
        individual_revenue_query.scalar_subquery() + collective_revenue_query.scalar_subquery()
    )

    return db.session.execute(total_revenue_query).scalar() or 0.0


def get_venue_offers_stats(venue_id: int) -> sa.engine.Row:
    individual_offers_query = sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
        sa.select(
            sa.case(
                [
                    (offers_models.Offer.isActive.is_(True), "active"),
                    (offers_models.Offer.isActive.is_(False), "inactive"),
                ]
            ).label("status"),
            sa.func.count(offers_models.Offer.id).label("number"),
        )
        .select_from(offerers_models.Venue)
        .outerjoin(offers_models.Offer)
        .filter(
            offerers_models.Venue.id == venue_id,
            offers_models.Offer.validation == offers_models.OfferValidationStatus.APPROVED.value,
        )
        .group_by(offers_models.Offer.isActive)
        .subquery()
    )
    collective_offers_query = sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
        sa.select(
            sa.case(
                [
                    (educational_models.CollectiveOffer.isActive.is_(True), "active"),
                    (educational_models.CollectiveOffer.isActive.is_(False), "inactive"),
                ]
            ).label("status"),
            sa.func.count(educational_models.CollectiveOffer.id).label("number"),
        )
        .select_from(offerers_models.Venue)
        .outerjoin(educational_models.CollectiveOffer)
        .filter(
            offerers_models.Venue.id == venue_id,
            educational_models.CollectiveOffer.validation == offers_models.OfferValidationStatus.APPROVED.value,
        )
        .group_by(educational_models.CollectiveOffer.isActive)
        .subquery()
    )

    offers_stats_query = (
        sa.select(
            providers_models.Provider.name,
            providers_models.VenueProvider.lastSyncDate,
            individual_offers_query.scalar_subquery().label("individual_offers"),
            collective_offers_query.scalar_subquery().label("collective_offers"),
        )
        .select_from(
            offerers_models.Venue,
        )
        .outerjoin(
            providers_models.VenueProvider,
            providers_models.VenueProvider.venueId == offerers_models.Venue.id,
        )
        .outerjoin(
            providers_models.Provider,
            providers_models.VenueProvider.providerId == providers_models.Provider.id,
        )
        .filter(
            providers_models.Venue.id == venue_id,
        )
    )

    return db.session.execute(offers_stats_query).one_or_none()


def count_offerers_by_validation_status() -> dict[str, int]:
    stats = dict(
        offerers_models.Offerer.query.with_entities(
            offerers_models.Offerer.validationStatus,
            sa.func.count(offerers_models.Offerer.validationStatus).label("count"),
        )
        .group_by(offerers_models.Offerer.validationStatus)
        .all()
    )

    # Ensure that the result includes every status, even if no offerer has this status
    return {status.name: stats.get(status, 0) for status in ValidationStatus}


def _filter_on_validation_status_legacy(
    query: sa.orm.Query, filter_dict: dict, cls: typing.Type[offerers_models.ValidationStatusMixin]
) -> sa.orm.Query:
    # This function becomes deprecated when backoffice v2 is stopped
    status_list = filter_dict.get("status")
    if status_list:
        statuses = []
        for status in status_list:
            try:
                statuses.append(ValidationStatus(status))
            except ValueError:
                pass  # ignore wrong value
        query = query.filter(cls.validationStatus.in_(statuses))
    else:
        query = query.filter(cls.isWaitingForValidation)

    return query


def list_offerers_to_be_validated_legacy(
    search_query: str | None, filter_: list[dict[str, typing.Any]]
) -> sa.orm.Query:
    # This function becomes deprecated when backoffice v2 is stopped
    query = offerers_models.Offerer.query.options(
        sa.orm.joinedload(offerers_models.Offerer.UserOfferers).joinedload(offerers_models.UserOfferer.user),
        sa.orm.joinedload(offerers_models.Offerer.tags),
        sa.orm.joinedload(offerers_models.Offerer.action_history).joinedload(history_models.ActionHistory.authorUser),
    )

    if search_query:
        if search_query.isnumeric():
            if len(search_query) != 9:
                raise exceptions.InvalidSiren("Le SIREN doit faire 9 caractères")
            query = query.filter(offerers_models.Offerer.siren == search_query)
        else:
            name = search_query.replace(" ", "%").replace("-", "%")
            name = clean_accents(name)
            query = query.filter(sa.func.unaccent(offerers_models.Offerer.name).ilike(f"%{name}%"))

    filter_dict = {f["field"]: f["value"] for f in filter_}

    query = _filter_on_validation_status_legacy(query, filter_dict, offerers_models.Offerer)

    tags = filter_dict.get("tags")
    if tags:
        tagged_offerers = (
            sa.select(offerers_models.Offerer.id, sa.func.array_agg(offerers_models.OffererTag.label).label("tags"))
            .join(
                offerers_models.OffererTagMapping,
                offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
            )
            .join(
                offerers_models.OffererTag,
                offerers_models.OffererTag.id == offerers_models.OffererTagMapping.tagId,
            )
            .group_by(
                offerers_models.Offerer.id,
            )
            .cte()
        )

        query = query.join(tagged_offerers, tagged_offerers.c.id == offerers_models.Offerer.id).filter(
            sa.and_(*(tagged_offerers.c.tags.any(tag) for tag in tags))
        )

    from_date = filter_dict.get("fromDate")
    if from_date:
        try:
            min_datetime = datetime.combine(date.fromisoformat(from_date), datetime.min.time())
        except ValueError:
            raise ApiErrors({"filter": "Le format de date est invalide"})
        query = query.filter(offerers_models.Offerer.dateCreated >= min_datetime)

    to_date = filter_dict.get("toDate")
    if to_date:
        try:
            max_datetime = datetime.combine(date.fromisoformat(to_date), datetime.max.time())
        except ValueError:
            raise ApiErrors({"filter": "Le format de date est invalide"})
        query = query.filter(offerers_models.Offerer.dateCreated <= max_datetime)

    return query


def _apply_query_filters(
    query: sa.orm.Query,
    q: str | None,  # search query
    regions: list[str] | None,
    tags: list[offerers_models.OffererTag] | None,
    status: list[ValidationStatus] | None,
    from_datetime: datetime | None,
    to_datetime: datetime | None,
    cls: typing.Type[offerers_models.Offerer | offerers_models.UserOfferer],
    offerer_id_column: sa.orm.InstrumentedAttribute,
) -> sa.orm.Query:
    if q:
        sanitized_q = email_utils.sanitize_email(q)

        if sanitized_q.isnumeric():
            num_digits = len(sanitized_q)
            if num_digits == 9:
                query = query.filter(offerers_models.Offerer.siren == sanitized_q)
            elif num_digits == 5:
                query = query.filter(offerers_models.Offerer.postalCode == sanitized_q)
            elif num_digits in (2, 3):
                query = query.filter(offerers_models.Offerer.departementCode == sanitized_q)
            else:
                raise exceptions.InvalidSiren(
                    "Le nombre de chiffres ne correspond pas à un SIREN, code postal ou département"
                )
        elif email_utils.is_valid_email(sanitized_q):
            query = query.filter(users_models.User.email == sanitized_q)
        else:
            name = q.replace(" ", "%").replace("-", "%")
            name = clean_accents(name)
            query = query.filter(
                sa.or_(
                    sa.func.unaccent(offerers_models.Offerer.name).ilike(f"%{name}%"),
                    sa.func.unaccent(offerers_models.Offerer.city).ilike(f"%{name}%"),
                    sa.func.unaccent(
                        sa.func.concat(users_models.User.firstName, " ", users_models.User.lastName)
                    ).ilike(f"%{name}%"),
                )
            )

    if status:
        query = query.filter(cls.validationStatus.in_(status))  # type: ignore [union-attr]

    if tags:
        tagged_offerers = (
            sa.select(offerers_models.Offerer.id, sa.func.array_agg(offerers_models.OffererTag.id).label("tags"))
            .join(
                offerers_models.OffererTagMapping,
                offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
            )
            .join(
                offerers_models.OffererTag,
                offerers_models.OffererTag.id == offerers_models.OffererTagMapping.tagId,
            )
            .group_by(
                offerers_models.Offerer.id,
            )
            .cte()
        )

        query = query.join(tagged_offerers, tagged_offerers.c.id == offerer_id_column).filter(
            sa.and_(*(tagged_offerers.c.tags.any(tag.id) for tag in tags))
        )

    if from_datetime:
        query = query.filter(cls.dateCreated >= from_datetime)

    if to_datetime:
        query = query.filter(cls.dateCreated <= to_datetime)

    if regions:
        department_codes: list[str] = []
        for region in regions:
            department_codes += get_department_codes_for_region(region)
        query = query.filter(offerers_models.Offerer.departementCode.in_(department_codes))  # type: ignore [attr-defined]

    return query


def list_offerers_to_be_validated(
    q: str | None,  # search query
    regions: list[str] | None = None,
    tags: list[offerers_models.OffererTag] | None = None,
    status: list[ValidationStatus] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
) -> sa.orm.Query:
    query = offerers_models.Offerer.query.options(
        sa.orm.joinedload(offerers_models.Offerer.UserOfferers).joinedload(offerers_models.UserOfferer.user),
        sa.orm.joinedload(offerers_models.Offerer.tags),
        sa.orm.joinedload(offerers_models.Offerer.action_history).joinedload(history_models.ActionHistory.authorUser),
    )

    if q:
        if email_utils.is_valid_email(email_utils.sanitize_email(q)):
            # Filter by attached user email address
            query = query.join(offerers_models.UserOfferer).join(users_models.User)
        else:
            # outerjoin so that we filter on offerer name entities which may have no user attached
            query = query.outerjoin(offerers_models.UserOfferer).outerjoin(users_models.User)

    query = _apply_query_filters(
        query, q, regions, tags, status, from_datetime, to_datetime, offerers_models.Offerer, offerers_models.Offerer.id
    )

    return query.distinct()


def is_top_actor(offerer: offerers_models.Offerer) -> bool:
    for tag in offerer.tags:
        if tag.name == "top-acteur":
            return True
    return False


def list_users_offerers_to_be_validated_legacy(filter_: list[dict[str, typing.Any]]) -> sa.orm.Query:
    # This function becomes deprecated when backoffice v2 is stopped
    query = offerers_models.UserOfferer.query.options(
        sa.orm.joinedload(offerers_models.UserOfferer.user),
        sa.orm.joinedload(offerers_models.UserOfferer.offerer)
        .joinedload(offerers_models.Offerer.action_history)
        .joinedload(history_models.ActionHistory.authorUser),
        sa.orm.joinedload(offerers_models.UserOfferer.offerer)
        .joinedload(offerers_models.Offerer.UserOfferers)
        .joinedload(offerers_models.UserOfferer.user),
    )

    filter_dict = {f["field"]: f["value"] for f in filter_}
    query = _filter_on_validation_status_legacy(query, filter_dict, offerers_models.UserOfferer)

    return query


def list_users_offerers_to_be_validated(
    q: str | None,  # search query
    regions: list[str] | None = None,
    tags: list[offerers_models.OffererTag] | None = None,
    status: list[ValidationStatus] | None = None,
    offerer_status: list[ValidationStatus] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
) -> sa.orm.Query:
    query = (
        offerers_models.UserOfferer.query.options(
            sa.orm.joinedload(offerers_models.UserOfferer.user),
            sa.orm.joinedload(offerers_models.UserOfferer.offerer)
            .joinedload(offerers_models.Offerer.action_history)
            .joinedload(history_models.ActionHistory.authorUser),
            sa.orm.joinedload(offerers_models.UserOfferer.offerer).joinedload(offerers_models.Offerer.UserOfferers),
            sa.orm.joinedload(offerers_models.UserOfferer.offerer)
            .joinedload(offerers_models.Offerer.UserOfferers)
            .joinedload(offerers_models.UserOfferer.user),
        )
        .join(users_models.User)
        .join(offerers_models.Offerer)
    )

    if offerer_status:
        query = query.filter(offerers_models.Offerer.validationStatus.in_(offerer_status))

    return _apply_query_filters(
        query,
        q,
        regions,
        tags,
        status,
        from_datetime,
        to_datetime,
        offerers_models.UserOfferer,
        offerers_models.UserOfferer.offererId,
    )


def update_offerer_tag(
    offerer_tag: models.OffererTag,
    name: str | T_UNCHANGED = UNCHANGED,
    label: str | T_UNCHANGED = UNCHANGED,
    description: str | T_UNCHANGED = UNCHANGED,
    categories: list[models.OffererTagCategory] | T_UNCHANGED = UNCHANGED,
) -> None:

    if name is not UNCHANGED:
        offerer_tag.name = name
    if label is not UNCHANGED:
        offerer_tag.label = label
    if description is not UNCHANGED:
        offerer_tag.description = description
    if categories is not UNCHANGED:
        if set(offerer_tag.categories) != set(categories):
            offerer_tag.categories = categories

    db.session.add(offerer_tag)
    db.session.commit()


def get_metabase_stats_iframe_url(
    offerer: models.Offerer,
    venues: typing.Sequence[models.Venue],
) -> str:
    """Generate a JWT-secured URL to a Metabase dashboard that shows
    statistics about one or more venues.
    """
    if not {venue.managingOffererId for venue in venues}.issubset({offerer.id}):
        raise ValueError("Cannot specify venue of another offerer")
    payload = {
        "resource": {"dashboard": settings.METABASE_DASHBOARD_ID},
        "params": {"siren": [offerer.siren], "venueid": [str(venue.id) for venue in venues]},
        # The dashboard token expires after 10 min. After that delay,
        # the user has to refresh their page to interact with the
        # dashbord (e.g to export content).
        "exp": round(time.time()) + (60 * 10),
    }
    token = jwt.encode(payload, settings.METABASE_SECRET_KEY, algorithm="HS256")
    return f"{settings.METABASE_SITE_URL}/embed/dashboard/{token}#bordered=false&titled=false"
