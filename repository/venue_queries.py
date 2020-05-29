from typing import List

from sqlalchemy.sql import selectable

from models import VenueSQLEntity, Offer


def find_by_id(venue_id: int) -> VenueSQLEntity:
    return VenueSQLEntity.query.filter_by(id=venue_id).first()


def find_by_offer_id(offer_id):
    return VenueSQLEntity.query \
        .join(Offer) \
        .filter(Offer.id == offer_id) \
        .first()


def find_by_siret(siret):
    return VenueSQLEntity.query.filter_by(siret=siret).first()


def find_by_managing_offerer_id(offerer_id: int) -> VenueSQLEntity:
    return VenueSQLEntity.query.filter_by(managingOffererId=offerer_id).first()


def find_by_managing_offerer_id_and_siret(offerer_id: int, siret: str) -> VenueSQLEntity:
    return VenueSQLEntity.query \
        .filter_by(managingOffererId=offerer_id) \
        .filter_by(siret=siret) \
        .one_or_none()


def get_only_venue_ids_for_department_codes(departement_codes: List[str]) -> selectable.Alias:
    return VenueSQLEntity.query \
        .filter(VenueSQLEntity.departementCode.in_(departement_codes)) \
        .with_entities(VenueSQLEntity.id) \
        .subquery()


def find_by_offerer_id_and_is_virtual(offrer_id: int):
    return VenueSQLEntity.query \
        .filter_by(managingOffererId=offrer_id, isVirtual=True) \
        .first()
