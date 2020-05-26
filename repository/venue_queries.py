from datetime import datetime
from typing import List

from sqlalchemy import and_, func
from sqlalchemy.sql import selectable

from models import Venue, Offer, StockSQLEntity, Offerer, UserOfferer, UserSQLEntity
from models.activity import load_activity
from models.db import db
from sqlalchemy import func


def find_by_id(venue_id: int) -> Venue:
    return Venue.query.filter_by(id=venue_id).first()


def find_by_offer_id(offer_id):
    return Venue.query \
        .join(Offer) \
        .filter(Offer.id == offer_id) \
        .first()


def find_by_siret(siret):
    return Venue.query.filter_by(siret=siret).first()


def find_by_managing_offerer_id(offerer_id: int) -> Venue:
    return Venue.query.filter_by(managingOffererId=offerer_id).first()


def find_by_managing_offerer_id_and_siret(offerer_id: int, siret: str) -> Venue:
    return Venue.query \
        .filter_by(managingOffererId=offerer_id) \
        .filter_by(siret=siret) \
        .one_or_none()


def find_by_managing_user(user: UserSQLEntity) -> List[Venue]:
    return Venue.query \
        .join(Offerer) \
        .join(UserOfferer) \
        .join(UserSQLEntity) \
        .filter(UserSQLEntity.id == user.id).all()


def get_only_venue_ids_for_department_codes(departement_codes: List[str]) -> selectable.Alias:
    return Venue.query \
        .filter(Venue.departementCode.in_(departement_codes)) \
        .with_entities(Venue.id) \
        .subquery()


def find_by_offerer_id_and_is_virtual(offrer_id: int):
    return Venue.query \
        .filter_by(managingOffererId=offrer_id, isVirtual=True) \
        .first()
