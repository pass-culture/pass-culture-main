from datetime import datetime
import logging
import secrets
import typing
from typing import Optional

from pcapi import settings
from pcapi.core import search
from pcapi.core.mails import MailServiceException
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueContact
from pcapi.core.offerers.models import VenueType
from pcapi.core.offerers.repository import find_by_siren
from pcapi.core.offerers.repository import find_offerer_by_validation_token
from pcapi.core.offerers.repository import find_user_offerer_by_validation_token
from pcapi.core.users.models import User
from pcapi.core.users.repository import get_user_with_validated_attachment_by_offerer
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.domain.pro_emails import send_attachment_validation_email_to_pro_offerer
from pcapi.domain.pro_emails import send_validation_confirmation_email_to_pro
from pcapi.models.db import db
from pcapi.repository import repository
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.offerers_serialize import CreateOffererQueryModel
from pcapi.routes.serialization.venues_serialize import PostVenueBodyModel
from pcapi.utils import crypto

from . import validation
from .exceptions import ApiKeyCountMaxReached
from .exceptions import ApiKeyDeletionDenied
from .exceptions import ApiKeyPrefixGenerationError
from .exceptions import ValidationTokenNotFoundError


logger = logging.getLogger(__name__)

UNCHANGED = object()
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "postalCode", "city", "latitude", "longitude"]
API_KEY_SEPARATOR = "_"


def create_digital_venue(offerer: Offerer) -> Venue:
    digital_venue = Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeId = _get_digital_venue_type_id()
    digital_venue.managingOfferer = offerer
    return digital_venue


def _get_digital_venue_type_id() -> int:
    return VenueType.query.filter_by(label="Offre numérique").one().id


def update_venue(venue: Venue, **attrs: typing.Any) -> Venue:
    validation.validate_coordinates(attrs.get("latitude"), attrs.get("longitude"))
    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    if not modifications:
        return venue

    validation.check_venue_edition(modifications, venue)
    venue.populate_from_dict(modifications)

    repository.save(venue)

    indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)

    if indexing_modifications_fields:
        search.async_index_venue_ids([venue.id])

    return venue


def upsert_venue_contact(venue: Venue, contact_data: venues_serialize.VenueContactModel) -> Venue:
    """
    Create and attach a VenueContact to a Venue if it has none.
    Update (replace) an existing VenueContact otherwise.
    """
    venue_contact = venue.contact
    if not venue_contact:
        venue_contact = VenueContact(venue=venue)

    venue_contact.email = contact_data.email
    venue_contact.website = contact_data.website
    venue_contact.phone_number = contact_data.phone_number
    venue_contact.social_medias = contact_data.social_medias or {}

    repository.save(venue_contact)
    return venue


def create_venue(venue_data: PostVenueBodyModel) -> Venue:
    data = venue_data.dict(by_alias=True)
    venue = Venue()
    venue.populate_from_dict(data)

    repository.save(venue)

    return venue


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


def create_offerer(user: User, offerer_informations: CreateOffererQueryModel):
    offerer = find_by_siren(offerer_informations.siren)

    if offerer is not None:
        user_offerer = offerer.grant_access(user)
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
        user_offerer = offerer.grant_access(user)
        repository.save(offerer, digital_venue, user_offerer)

    _send_to_pc_admin_offerer_to_validate_email(offerer, user_offerer)

    return user_offerer


def _send_to_pc_admin_offerer_to_validate_email(offerer: Offerer, user_offerer: UserOfferer) -> None:
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer)
    except MailServiceException as mail_service_exception:
        logger.exception("Could not send validation email to offerer", extra={"exc": str(mail_service_exception)})


def validate_offerer_attachment(token: str) -> None:
    user_offerer = find_user_offerer_by_validation_token(token)
    if user_offerer is None:
        raise ValidationTokenNotFoundError()

    user_offerer.validationToken = None
    user_offerer.user.add_pro_role()
    repository.save(user_offerer)

    try:
        send_attachment_validation_email_to_pro_offerer(user_offerer)
    except MailServiceException as mail_service_exception:
        logger.exception(
            "Could not send attachment validation email to offerer", extra={"exc": str(mail_service_exception)}
        )


def validate_offerer(token: str) -> None:
    offerer = find_offerer_by_validation_token(token)
    if offerer is None:
        raise ValidationTokenNotFoundError()

    applicant = get_user_with_validated_attachment_by_offerer(offerer)
    offerer.validationToken = None
    offerer.dateValidated = datetime.utcnow()
    applicant.add_pro_role()
    managed_venues = offerer.managedVenues

    repository.save(offerer)
    search.async_index_venue_ids([venue.id for venue in managed_venues])

    try:
        send_validation_confirmation_email_to_pro(offerer)
    except MailServiceException as mail_service_exception:
        logger.exception(
            "Could not send validation confirmation email to offerer", extra={"exc": str(mail_service_exception)}
        )
