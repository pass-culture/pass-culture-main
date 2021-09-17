from typing import Optional

from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueLabel
from pcapi.core.offerers.models import VenueType
from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer


def get_all_venue_labels() -> list[VenueLabel]:
    return VenueLabel.query.all()


def get_all_venue_types() -> list[VenueType]:
    return VenueType.query.all()


def get_all_offerers_for_user(user: User, filters: dict) -> list[Offerer]:
    query = Offerer.query.filter(Offerer.isActive.is_(True))

    if not user.isAdmin:
        query = query.join(UserOfferer, UserOfferer.offererId == Offerer.id).filter(UserOfferer.userId == user.id)

    if "validated" in filters and filters["validated"] is not None:
        if filters["validated"] == True:
            query = query.filter(Offerer.validationToken.is_(None))
        else:
            query = query.filter(Offerer.validationToken.isnot(None))

    if "validated_for_user" in filters and filters["validated_for_user"] is not None:
        if filters["validated_for_user"] == True:
            query = query.filter(UserOfferer.validationToken.is_(None))
        else:
            query = query.filter(UserOfferer.validationToken.isnot(None))

    return query.all()


def get_filtered_venues(
    pro_user_id: int,
    user_is_admin: bool,
    active_offerers_only: Optional[bool] = False,
    offerer_id: Optional[int] = None,
    validated_offerer: Optional[bool] = None,
    validated_offerer_for_user: Optional[bool] = None,
) -> list[Venue]:
    query = Venue.query.join(Offerer, Offerer.id == Venue.managingOffererId).join(
        UserOfferer, UserOfferer.offererId == Offerer.id
    )
    if not user_is_admin:
        query = query.filter(UserOfferer.userId == pro_user_id)

    if validated_offerer is not None:
        if validated_offerer:
            query = query.filter(Offerer.validationToken.is_(None))
        else:
            query = query.filter(Offerer.validationToken.isnot(None))
    if validated_offerer_for_user is not None:
        if validated_offerer_for_user:
            query = query.filter(UserOfferer.validationToken.is_(None))
        else:
            query = query.filter(UserOfferer.validationToken.isnot(None))

    if active_offerers_only:
        query = query.filter(Offerer.isActive.is_(True))

    if offerer_id:
        query = query.filter(Venue.managingOffererId == offerer_id)

    return query.order_by(Venue.name).all()


def get_api_key_prefixes(offerer_id: int) -> list[str]:
    return [
        prefix or value[:8]
        for prefix, value in ApiKey.query.filter_by(offererId=offerer_id)
        .with_entities(ApiKey.prefix, ApiKey.value)
        .all()
        if prefix or value
    ]


def find_offerer_by_siren(siren: str) -> Optional[Offerer]:
    return Offerer.query.filter_by(siren=siren).one_or_none()


def find_user_offerer_by_validation_token(token: str) -> Optional[UserOfferer]:
    return UserOfferer.query.filter_by(validationToken=token).one_or_none()


def find_offerer_by_validation_token(token: str) -> Optional[UserOfferer]:
    return Offerer.query.filter_by(validationToken=token).one_or_none()


def find_venue_by_id(venue_id: int) -> Optional[Venue]:
    return Venue.query.filter_by(id=venue_id).one_or_none()


def find_venue_by_siret(siret: str) -> Optional[Venue]:
    return Venue.query.filter_by(siret=siret).one_or_none()


def find_venue_by_managing_offerer_id(offerer_id: int) -> Optional[Venue]:
    return Venue.query.filter_by(managingOffererId=offerer_id).first()


def find_virtual_venue_by_offerer_id(offerer_id: int) -> Optional[Venue]:
    return Venue.query.filter_by(managingOffererId=offerer_id, isVirtual=True).first()
