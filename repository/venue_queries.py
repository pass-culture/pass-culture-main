from typing import List

from sqlalchemy.sql import selectable

from models import VenueSQLEntity, OfferSQLEntity, StockSQLEntity, Offerer, UserOfferer, UserSQLEntity
from models.activity import load_activity
from models.db import db
from repository.offerer_queries import _filter_by_sirens
from sqlalchemy import and_
from datetime import datetime


def find_by_id(venue_id: int) -> VenueSQLEntity:
    return VenueSQLEntity.query.filter_by(id=venue_id).first()


def find_by_offer_id(offer_id):
    return VenueSQLEntity.query \
        .join(OfferSQLEntity) \
        .filter(OfferSQLEntity.id == offer_id) \
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


def find_filtered_venues(sirens=None,
                         dpts=None,
                         zip_codes=None,
                         from_date=None,
                         to_date=None,
                         has_siret=None,
                         is_virtual=None,
                         offer_status=None,
                         is_validated=None,
                         has_validated_offerer=None,
                         has_offerer_with_siren=None,
                         has_validated_user_offerer=None,
                         has_validated_user=None):
    query = db.session.query(VenueSQLEntity)
    if dpts:
        query = _filter_by_dpts(query, dpts)

    if zip_codes:
        query = _filter_by_zipcodes(query, zip_codes)

    if from_date or to_date:
        query = _filter_by_date(query, from_date, to_date)

    if has_siret is not None:
        query = _filter_by_has_siret(query, has_siret)

    if is_virtual is not None:
        query = _filter_by_is_virtual(query, is_virtual)

    if offer_status:
        query = _filter_by_offer_status(query, offer_status)

    if is_validated is not None:
        query = _filter_by_is_validated(query, is_validated)

    if has_validated_offerer is not None or has_offerer_with_siren is not None \
            or has_validated_user_offerer is not None or has_validated_user is not None \
            or sirens is not None:
        query = query.join(Offerer)

    if sirens is not None:
        query = _filter_by_sirens(query, sirens)

    if has_validated_offerer is not None:
        query = _filter_by_has_validated_offerer(query, has_validated_offerer)

    if has_offerer_with_siren is not None:
        query = _filter_by_has_offerer_with_siren(
            query, has_offerer_with_siren)

    if has_validated_user_offerer is not None or has_validated_user is not None:
        query = query.join(UserOfferer)

    if has_validated_user_offerer is not None:
        query = _filter_by_has_validated_user_offerer(
            query, has_validated_user_offerer)

    if has_validated_user is not None:
        query = _filter_by_has_validated_user(query, has_validated_user)

    result = query.all()
    return result


def find_by_managing_user(user: UserSQLEntity) -> List[VenueSQLEntity]:
    return VenueSQLEntity.query \
        .join(Offerer) \
        .join(UserOfferer) \
        .join(UserSQLEntity) \
        .filter(UserSQLEntity.id == user.id).all()


def _filter_by_is_virtual(query, is_virtual):
    if is_virtual:
        query = query.filter(VenueSQLEntity.isVirtual == True)
    else:
        query = query.filter(VenueSQLEntity.isVirtual == False)

    return query


def _filter_by_has_validated_offerer(query, has_validated_offerer):
    is_valid = Offerer.validationToken == None
    if has_validated_offerer:
        query = query.filter(is_valid)
    else:
        query = query.filter(~is_valid)

    return query


def _filter_by_has_offerer_with_siren(query, has_offerer_with_siren):
    has_siren = Offerer.siren != None
    if has_offerer_with_siren:
        query = query.filter(has_siren)
    else:
        query = query.filter(~has_siren)

    return query


def _filter_by_has_validated_user_offerer(query, has_validated_user_offerer):
    is_valid = UserOfferer.validationToken == None
    if has_validated_user_offerer:
        query = query.filter(Offerer.users.any(is_valid))
    else:
        query = query.filter(~Offerer.users.any(is_valid))

    return query


def _filter_by_has_validated_user(query, has_validated_user):
    is_valid = UserSQLEntity.validationToken == None
    query = query.join(UserSQLEntity)
    if has_validated_user:
        query = query.filter(Offerer.users.any(is_valid))
    else:
        query = query.filter(~Offerer.users.any(is_valid))

    return query


def _filter_by_dpts(query, dpts):
    query = query.filter(VenueSQLEntity.departementCode.in_(dpts))
    return query


def _filter_by_zipcodes(query, zip_codes):
    query = query.filter(VenueSQLEntity.postalCode.in_(zip_codes))
    return query


def _filter_by_date(query, from_date=None, to_date=None):
    Activity = load_activity()
    is_on_table_venue = Activity.table_name == 'venue'
    is_insert = Activity.verb == 'insert'
    activity_data_id_matches_venue_id = Activity.data['id'].astext.cast(
        db.Integer) == VenueSQLEntity.id
    query = query.join(Activity, activity_data_id_matches_venue_id).filter(
        and_(is_on_table_venue, is_insert))

    if from_date:
        query = query.filter(Activity.issued_at >= from_date)
    if to_date:
        query = query.filter(Activity.issued_at <= to_date)
    return query


def _filter_by_has_siret(query, has_siret):
    if has_siret:
        query = query.filter(VenueSQLEntity.siret != None)
    else:
        query = query.filter(VenueSQLEntity.siret == None)
    return query


def _filter_by_is_validated(query, is_validated):
    if is_validated:
        query = query.filter(VenueSQLEntity.validationToken == None)
    else:
        query = query.filter(VenueSQLEntity.validationToken != None)
    return query


def _filter_by_offer_status(query, offer_status):
    if offer_status == 'ALL':
        query = query.join(OfferSQLEntity)
    elif offer_status == "WITHOUT":
        query = query.filter(~VenueSQLEntity.offers.any())

    elif offer_status == "VALID" or offer_status == "EXPIRED":
        query = query.join(OfferSQLEntity)
        is_not_soft_deleted_thing = StockSQLEntity.isSoftDeleted == False
        can_still_be_booked_thing = (
            (StockSQLEntity.bookingLimitDatetime == None) | (StockSQLEntity.bookingLimitDatetime >= datetime.utcnow()))
        is_available_thing = ((StockSQLEntity.quantity == None) | (StockSQLEntity.quantity > 0))

        query_1 = query.join(StockSQLEntity)
        query_2 = query.join(StockSQLEntity)

    if offer_status == "VALID":
        query_with_valid_event = query_1.filter(
            is_not_soft_deleted_thing & can_still_be_booked_thing & is_available_thing)
        query_with_valid_thing = query_2.filter(
            is_not_soft_deleted_thing & can_still_be_booked_thing & is_available_thing)
        query = query_with_valid_event.union_all(query_with_valid_thing)

    if offer_status == "EXPIRED":
        query_with_expired_event = query_1.filter(
            ~(is_not_soft_deleted_thing & can_still_be_booked_thing & is_available_thing))
        query_with_expired_thing = query_2.filter(
            ~(is_not_soft_deleted_thing & can_still_be_booked_thing & is_available_thing))
        query = query_with_expired_event.union_all(query_with_expired_thing)

    return query


def get_only_venue_ids_for_department_codes(departement_codes: List[str]) -> selectable.Alias:
    return VenueSQLEntity.query \
        .filter(VenueSQLEntity.departementCode.in_(departement_codes)) \
        .with_entities(VenueSQLEntity.id) \
        .subquery()


def find_by_offerer_id_and_is_virtual(offrer_id: int):
    return VenueSQLEntity.query \
        .filter_by(managingOffererId=offrer_id, isVirtual=True) \
        .first()
