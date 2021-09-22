import datetime
from typing import Optional

import sqlalchemy.orm as sqla_orm
from sqlalchemy.orm import Query
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.domain.ts_vector import create_filter_matching_all_keywords_in_any_model
from pcapi.domain.ts_vector import create_get_filter_matching_ts_query_in_any_model
from pcapi.models import db


def get_all_venue_labels() -> list[offerers_models.VenueLabel]:
    return offerers_models.VenueLabel.query.all()


def get_all_venue_types() -> list[offerers_models.VenueType]:
    return offerers_models.VenueType.query.all()


def get_all_offerers_for_user(user: User, filters: dict) -> list[offerers_models.Offerer]:
    query = offerers_models.Offerer.query.filter(offerers_models.Offerer.isActive.is_(True))

    if not user.isAdmin:
        query = query.join(
            offerers_models.UserOfferer, offerers_models.UserOfferer.offererId == offerers_models.Offerer.id
        ).filter(offerers_models.UserOfferer.userId == user.id)

    if "validated" in filters and filters["validated"] is not None:
        if filters["validated"] == True:
            query = query.filter(offerers_models.Offerer.validationToken.is_(None))
        else:
            query = query.filter(offerers_models.Offerer.validationToken.isnot(None))

    if "validated_for_user" in filters and filters["validated_for_user"] is not None:
        if filters["validated_for_user"] == True:
            query = query.filter(offerers_models.UserOfferer.validationToken.is_(None))
        else:
            query = query.filter(offerers_models.UserOfferer.validationToken.isnot(None))

    return query.all()


def get_filtered_venues(
    pro_user_id: int,
    user_is_admin: bool,
    active_offerers_only: Optional[bool] = False,
    offerer_id: Optional[int] = None,
    validated_offerer: Optional[bool] = None,
    validated_offerer_for_user: Optional[bool] = None,
) -> list[Venue]:
    query = (
        Venue.query.join(offerers_models.Offerer, offerers_models.Offerer.id == offerers_models.Venue.managingOffererId)
        .join(offerers_models.UserOfferer, offerers_models.UserOfferer.offererId == offerers_models.Offerer.id)
        .options(sqla_orm.joinedload(offerers_models.Venue.managingOfferer))
    )
    if not user_is_admin:
        query = query.filter(offerers_models.UserOfferer.userId == pro_user_id)

    if validated_offerer is not None:
        if validated_offerer:
            query = query.filter(offerers_models.Offerer.validationToken.is_(None))
        else:
            query = query.filter(offerers_models.Offerer.validationToken.isnot(None))
    if validated_offerer_for_user is not None:
        if validated_offerer_for_user:
            query = query.filter(offerers_models.UserOfferer.validationToken.is_(None))
        else:
            query = query.filter(offerers_models.UserOfferer.validationToken.isnot(None))

    if active_offerers_only:
        query = query.filter(offerers_models.Offerer.isActive.is_(True))

    if offerer_id:
        query = query.filter(offerers_models.Venue.managingOffererId == offerer_id)

    return query.order_by(offerers_models.Venue.name).all()


def get_api_key_prefixes(offerer_id: int) -> list[str]:
    return [
        prefix or value[:8]
        for prefix, value in offerers_models.ApiKey.query.filter_by(offererId=offerer_id)
        .with_entities(offerers_models.ApiKey.prefix, offerers_models.ApiKey.value)
        .all()
        if prefix or value
    ]


def find_offerer_by_siren(siren: str) -> Optional[offerers_models.Offerer]:
    return offerers_models.Offerer.query.filter_by(siren=siren).one_or_none()


def find_user_offerer_by_validation_token(token: str) -> Optional[offerers_models.UserOfferer]:
    return offerers_models.UserOfferer.query.filter_by(validationToken=token).one_or_none()


def find_offerer_by_validation_token(token: str) -> Optional[offerers_models.UserOfferer]:
    return offerers_models.Offerer.query.filter_by(validationToken=token).one_or_none()


def find_venue_by_id(venue_id: int) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()


def find_venue_by_siret(siret: str) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(siret=siret).one_or_none()


def find_venue_by_managing_offerer_id(offerer_id: int) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).first()


def find_virtual_venue_by_offerer_id(offerer_id: int) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(managingOffererId=offerer_id, isVirtual=True).first()






get_filter_matching_ts_query_for_offerer = create_get_filter_matching_ts_query_in_any_model(
    offerers_models.Offerer, offerers_models.Venue
)


def get_by_offer_id(offer_id: int) -> Optional[offerers_models.Offerer]:
    return offerers_models.Offerer.query.join(offerers_models.Venue).join(Offer).filter_by(id=offer_id).one_or_none()


def find_new_offerer_user_email(offerer_id: int) -> str:
    result_tuple = models.UserOfferer.query.filter_by(offererId=offerer_id).join(User).with_entities(User.email).first()
    if result_tuple:
        return result_tuple[0]
    raise exceptions.CannotFindOffererUserEmail


def filter_offerers_with_keywords_string(query: Query, keywords_string: str) -> Query:
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_offerer, keywords_string
    )
    query = query.filter(keywords_filter)
    return query


def check_if_siren_already_exists(siren: str) -> bool:
    return db.session.query(db.session.query(models.Offerer.id).filter(models.Offerer.siren == siren).exists())


def get_offerers_by_date_validated(date_validated: datetime.date) -> list[offerers_models.Offerer]:
    from_date = datetime.datetime.combine(date_validated, datetime.datetime.min.time())
    to = datetime.datetime.combine(date_validated, datetime.datetime.max.time())

    return offerers_models.Offerer.query.filter(offerers_models.Offerer.dateValidated.between(from_date, to)).all()
