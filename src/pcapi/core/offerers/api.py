import secrets
from typing import Optional

import bcrypt

from pcapi import settings
from pcapi.core import search
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueType
from pcapi.core.users.models import User
from pcapi.domain.iris import link_valid_venue_to_irises
from pcapi.models.db import db
from pcapi.repository import repository
from pcapi.repository.iris_venues_queries import delete_venue_from_iris_venues
from pcapi.routes.serialization.venues_serialize import PostVenueBodyModel

from . import validation
from .exceptions import ApiKeyCountMaxReached
from .exceptions import ApiKeyDeletionDenied
from .exceptions import ApiKeyPrefixGenerationError


UNCHANGED = object()
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "city"]
API_KEY_SEPARATOR = "_"


def create_digital_venue(offerer):
    digital_venue = Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeId = _get_digital_venue_type_id()
    digital_venue.managingOfferer = offerer
    return digital_venue


def _get_digital_venue_type_id() -> int:
    return VenueType.query.filter_by(label="Offre numérique").one().id


def update_venue(
    venue: Venue,
    address: str = UNCHANGED,
    name: str = UNCHANGED,
    siret: str = UNCHANGED,
    latitude: float = UNCHANGED,
    longitude: float = UNCHANGED,
    bookingEmail: str = UNCHANGED,
    postalCode: str = UNCHANGED,
    city: str = UNCHANGED,
    publicName: str = UNCHANGED,
    comment: str = UNCHANGED,
    venueTypeId: int = UNCHANGED,
    venueLabelId: int = UNCHANGED,
) -> Venue:
    validation.validate_coordinates(
        latitude if latitude is not UNCHANGED else None,
        longitude if latitude is not UNCHANGED else None,
    )

    # fmt: off
    modifications = {
        field: new_value
        for field, new_value in locals().items()
        if field != 'venue'
        and new_value is not UNCHANGED  # has the user provided a value for this field
        and getattr(venue, field) != new_value  # is the value different from what we have on database?
    }
    # fmt: on
    if not modifications:
        return venue

    validation.check_venue_edition(modifications, venue)
    venue.populate_from_dict(modifications)

    if not venue.isVirtual:
        delete_venue_from_iris_venues(venue.id)

    repository.save(venue)

    link_valid_venue_to_irises(venue)

    indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)

    if indexing_modifications_fields:
        search.async_index_venue_ids([venue.id])

    return venue


def create_venue(venue_data: PostVenueBodyModel) -> Venue:
    data = venue_data.dict(by_alias=True)
    venue = Venue()
    venue.populate_from_dict(data)

    repository.save(venue)

    link_valid_venue_to_irises(venue=venue)

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
    key = ApiKey(
        offererId=offerer_id, prefix=prefix, secret=bcrypt.hashpw(_encode_clear_secret(clear_secret), bcrypt.gensalt())
    )

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

    return api_key if bcrypt.checkpw(_encode_clear_secret(clear_secret), api_key.secret) else None


def _create_prefix(env: str, prefix_identifier: str) -> str:
    return f"{env}{API_KEY_SEPARATOR}{prefix_identifier}"


def _encode_clear_secret(secret: str) -> bytes:
    return secret.encode("utf-8")


def delete_api_key_by_user(user: User, api_key_prefix: str) -> None:
    api_key = ApiKey.query.filter_by(prefix=api_key_prefix).one()

    if not user.has_access(api_key.offererId):
        raise ApiKeyDeletionDenied()

    db.session.delete(api_key)
