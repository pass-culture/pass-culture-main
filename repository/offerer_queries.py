from datetime import datetime

from flask_login import current_user
from sqlalchemy import or_

from domain.keywords import create_filter_matching_all_keywords_in_any_model, \
    create_get_filter_matching_ts_query_in_any_model
from models import Offerer, VenueSQLEntity, Offer, UserOfferer, UserSQLEntity, StockSQLEntity, ThingType, EventType
from models.db import db

get_filter_matching_ts_query_for_offerer = create_get_filter_matching_ts_query_in_any_model(
    Offerer,
    VenueSQLEntity
)


def count_offerer() -> int:
    return _query_offerers_with_user_offerer().count()


def count_offerer_by_departement(departement_code: str) -> int:
    return _query_offerers_with_user_offerer() \
        .join(VenueSQLEntity, VenueSQLEntity.managingOffererId == Offerer.id) \
        .filter(VenueSQLEntity.departementCode == departement_code) \
        .count()


def count_offerer_with_stock() -> int:
    return _query_offerers_with_stock().count()


def count_offerer_with_stock_by_departement(departement_code: str) -> int:
    return _query_offerers_with_stock() \
        .filter(VenueSQLEntity.departementCode == departement_code) \
        .count()


def find_by_id(id):
    return Offerer.query.filter_by(id=id).first()


def find_by_siren(siren):
    return Offerer.query.filter_by(siren=siren).first()


def get_by_offer_id(offer_id):
    return Offerer.query.join(VenueSQLEntity).join(Offer).filter_by(id=offer_id).first()


def find_new_offerer_user_email(offerer_id):
    return UserOfferer.query \
        .filter_by(offererId=offerer_id) \
        .join(UserSQLEntity) \
        .with_entities(UserSQLEntity.email) \
        .first()[0]


def find_all_offerers_with_managing_user_information():
    query = db.session.query(Offerer.id, Offerer.name, Offerer.siren, Offerer.postalCode, Offerer.city, UserSQLEntity.firstName,
                             UserSQLEntity.lastName, UserSQLEntity.email, UserSQLEntity.phoneNumber, UserSQLEntity.postalCode) \
        .join(UserOfferer, Offerer.id == UserOfferer.offererId) \
        .join(UserSQLEntity, UserSQLEntity.id == UserOfferer.userId)

    result = query.order_by(Offerer.name, UserSQLEntity.email).all()
    return result


def find_all_offerers_with_managing_user_information_and_venue():
    query = db.session.query(Offerer.id, Offerer.name, Offerer.siren, Offerer.postalCode, Offerer.city, VenueSQLEntity.name,
                             VenueSQLEntity.bookingEmail, VenueSQLEntity.postalCode, UserSQLEntity.firstName, UserSQLEntity.lastName, UserSQLEntity.email,
                             UserSQLEntity.phoneNumber, UserSQLEntity.postalCode) \
        .join(UserOfferer, Offerer.id == UserOfferer.offererId) \
        .join(UserSQLEntity, UserSQLEntity.id == UserOfferer.userId) \
        .join(VenueSQLEntity)

    result = query.order_by(Offerer.name, VenueSQLEntity.name, UserSQLEntity.email).all()
    return result


def find_all_offerers_with_managing_user_information_and_not_virtual_venue():
    query = db.session.query(Offerer.id, Offerer.name, Offerer.siren, Offerer.postalCode, Offerer.city, VenueSQLEntity.name,
                             VenueSQLEntity.bookingEmail, VenueSQLEntity.postalCode, UserSQLEntity.firstName, UserSQLEntity.lastName, UserSQLEntity.email,
                             UserSQLEntity.phoneNumber, UserSQLEntity.postalCode) \
        .join(UserOfferer, Offerer.id == UserOfferer.offererId) \
        .join(UserSQLEntity, UserSQLEntity.id == UserOfferer.userId) \
        .join(VenueSQLEntity)

    result = query.filter(VenueSQLEntity.isVirtual == False).order_by(
        Offerer.name, VenueSQLEntity.name, UserSQLEntity.email).all()
    return result


def find_all_offerers_with_venue():
    query = db.session.query(Offerer.id, Offerer.name, VenueSQLEntity.id, VenueSQLEntity.name, VenueSQLEntity.bookingEmail, VenueSQLEntity.postalCode,
                             VenueSQLEntity.isVirtual) \
        .join(VenueSQLEntity)

    result = query.order_by(Offerer.name, VenueSQLEntity.name, VenueSQLEntity.id).all()
    return result


def find_all_pending_validation():
    user_offerer_pending_validation = UserOfferer.validationToken != None
    offerer_pending_validation = Offerer.validationToken != None
    venue_pending_validation = VenueSQLEntity.validationToken != None
    user_pending_validation = UserSQLEntity.validationToken != None

    result = Offerer.query \
        .join(UserOfferer) \
        .join(VenueSQLEntity) \
        .join(UserSQLEntity) \
        .filter(or_(user_offerer_pending_validation, offerer_pending_validation, venue_pending_validation,
                    user_pending_validation)) \
        .order_by(Offerer.id).all()

    return result


def find_first_by_user_offerer_id(user_offerer_id):
    return Offerer.query.join(UserOfferer).filter_by(id=user_offerer_id).first()


def find_filtered_offerers(sirens=None,
                           dpts=None,
                           zip_codes=None,
                           from_date=None,
                           to_date=None,
                           has_siren=None,
                           has_bank_information=None,
                           is_validated=None,
                           is_active=None,
                           has_not_virtual_venue=None,
                           has_validated_venue=None,
                           has_venue_with_siret=None,
                           offer_status=None,
                           has_validated_user=None,
                           has_validated_user_offerer=None):
    query = db.session.query(Offerer)
    if sirens is not None:
        query = _filter_by_sirens(query, sirens)

    if dpts is not None:
        query = _filter_by_dpts(query, dpts)

    if zip_codes is not None:
        query = _filter_by_zip_codes(query, zip_codes)

    if from_date is not None or to_date is not None:
        query = _filter_by_date(query, from_date, to_date)

    if has_siren is not None:
        query = _filter_by_has_siren(query, has_siren)

    if has_bank_information is not None:
        query = _filter_by_has_bank_information(query, has_bank_information)

    if is_validated is not None:
        query = _filter_by_is_validated(query, is_validated)

    if is_active is not None:
        query = _filter_by_is_active(query, is_active)

    if has_not_virtual_venue is not None or has_validated_venue is not None \
            or offer_status is not None or has_venue_with_siret is not None:
        query = query.join(VenueSQLEntity)

    if has_not_virtual_venue is not None:
        query = _filter_by_has_not_virtual_venue(query, has_not_virtual_venue)

    if has_validated_venue is not None:
        query = _filter_by_has_validated_venue(query, has_validated_venue)

    if has_venue_with_siret is not None:
        query = _filter_by_has_venue_with_siret(query, has_venue_with_siret)

    if offer_status is not None:
        query = _filter_by_offer_status(query, offer_status)

    if has_validated_user_offerer is not None or has_validated_user is not None:
        query = query.join(UserOfferer)

    if has_validated_user_offerer is not None:
        query = _filter_by_has_validated_user_offerer(
            query, has_validated_user_offerer)

    if has_validated_user is not None:
        query = query.join(UserSQLEntity)
        query = _filter_by_has_validated_user(query, has_validated_user)

    result = query.all()
    return result


def _filter_by_sirens(query, sirens):
    return query.filter(Offerer.siren.in_(sirens))


def _filter_by_dpts(query, dpts):
    dpts_filter = _create_filter_from_dpts_list(dpts)

    query = query.filter(dpts_filter)
    return query


def _create_filter_from_dpts_list(dpts):
    previous_dpts_filter = None
    dpts_filter = None
    final_dpts_filter = None

    for dpt in dpts:
        if dpts_filter is not None:
            previous_dpts_filter = dpts_filter
            if final_dpts_filter is not None:
                previous_dpts_filter = final_dpts_filter

        dpts_filter = Offerer.postalCode.like(dpt + '%')

        if previous_dpts_filter is not None:
            final_dpts_filter = previous_dpts_filter | dpts_filter

    return final_dpts_filter


def _filter_by_zip_codes(query, zip_codes):
    return query.filter(Offerer.postalCode.in_(zip_codes))


def _filter_by_date(query, from_date, to_date):
    if from_date:
        query = query.filter(Offerer.dateCreated >= from_date)
    if to_date:
        query = query.filter(Offerer.dateCreated <= to_date)
    return query


def _filter_by_has_siren(query, has_siren):
    if has_siren:
        query = query.filter(Offerer.siren != None)
    else:
        query = query.filter(Offerer.siren == None)
    return query


def _filter_by_is_validated(query, is_validated):
    if is_validated:
        query = query.filter(Offerer.validationToken == None)
    else:
        query = query.filter(Offerer.validationToken != None)
    return query


def _filter_by_has_bank_information(query, has_bank_information):
    if has_bank_information:
        query = query.filter(Offerer.bankInformation != None)
    else:
        query = query.filter(Offerer.bankInformation == None)
    return query


def _filter_by_is_active(query, is_active):
    if is_active:
        query = query.filter(Offerer.isActive)
    else:
        query = query.filter(~Offerer.isActive)
    return query


def _filter_by_has_not_virtual_venue(query, has_not_virtual_venue):
    is_not_virtual = VenueSQLEntity.isVirtual == False
    if has_not_virtual_venue:
        query = query.filter(Offerer.managedVenues.any(is_not_virtual))
    else:
        query = query.filter(~Offerer.managedVenues.any(is_not_virtual))
    return query


def _filter_by_has_validated_venue(query, has_validated_venue):
    is_valid = VenueSQLEntity.validationToken == None
    if has_validated_venue:
        query = query.filter(Offerer.managedVenues.any(is_valid))
    else:
        query = query.filter(~Offerer.managedVenues.any(is_valid))
    return query


def _filter_by_has_venue_with_siret(query, has_venue_with_siret):
    has_siret = VenueSQLEntity.siret != None
    if has_venue_with_siret:
        query = query.filter(Offerer.managedVenues.any(has_siret))
    else:
        query = query.filter(~Offerer.managedVenues.any(has_siret))
    return query


def _filter_by_offer_status(query, offer_status):
    if offer_status == 'ALL':
        query = query.join(Offer)
    elif offer_status == "WITHOUT":
        query = query.filter(~VenueSQLEntity.offers.any())

    elif offer_status == "VALID" or offer_status == "EXPIRED":
        query = query.join(Offer)
        can_still_be_booked_event = StockSQLEntity.bookingLimitDatetime >= datetime.utcnow()
        is_not_soft_deleted_thing = StockSQLEntity.isSoftDeleted == False
        can_still_be_booked_thing = ((StockSQLEntity.bookingLimitDatetime == None)
                                     | (StockSQLEntity.bookingLimitDatetime >= datetime.utcnow()))
        is_available_thing = ((StockSQLEntity.quantity == None) | (StockSQLEntity.quantity > 0))

        query_1 = query.join(StockSQLEntity)
        query_2 = query.join(StockSQLEntity)

    if offer_status == "VALID":
        query_with_valid_event = query_1.filter(is_not_soft_deleted_thing
                                                & can_still_be_booked_thing & is_available_thing)
        query_with_valid_thing = query_2.filter(is_not_soft_deleted_thing
                                                & can_still_be_booked_thing & is_available_thing)
        query = query_with_valid_event.union_all(query_with_valid_thing)

    if offer_status == "EXPIRED":
        query_with_expired_event = query_1.filter(~(is_not_soft_deleted_thing
                                                    & can_still_be_booked_thing & is_available_thing))
        query_with_expired_thing = query_2.filter(~(is_not_soft_deleted_thing
                                                    & can_still_be_booked_thing & is_available_thing))
        query = query_with_expired_event.union_all(query_with_expired_thing)

    return query


def _filter_by_has_validated_user_offerer(query, has_validated_user_offerer):
    is_valid = UserOfferer.validationToken == None
    if has_validated_user_offerer:
        query = query.filter(Offerer.UserOfferers.any(is_valid))
    else:
        query = query.filter(~Offerer.UserOfferers.any(is_valid))
    return query


def _filter_by_has_validated_user(query, has_validated_user):
    is_valid = UserSQLEntity.validationToken == None
    if has_validated_user:
        query = query.filter(Offerer.users.any(is_valid))
    else:
        query = query.filter(~Offerer.users.any(is_valid))
    return query


def filter_offerers_with_keywords_string(query, keywords_string):
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_offerer,
        keywords_string
    )
    query = query.filter(keywords_filter)
    return query


def check_if_siren_already_exists(siren):
    return Offerer.query.filter_by(siren=siren).count() > 0


def keep_offerers_with_at_least_one_physical_venue(query):
    return query.filter(Offerer.managedVenues.any(VenueSQLEntity.isVirtual == False))


def keep_offerers_with_no_physical_venue(query):
    is_not_virtual = VenueSQLEntity.isVirtual == False
    return query.filter(~Offerer.managedVenues.any(is_not_virtual))


def keep_offerers_with_no_validated_users(query):
    query = query.join(UserOfferer) \
        .join(UserSQLEntity) \
        .filter(~Offerer.UserOfferers.any(UserSQLEntity.validationToken == None))
    return query


def _query_offerers_with_user_offerer():
    return Offerer.query \
        .join(UserOfferer) \
        .distinct(Offerer.id)


def _query_offerers_with_stock():
    return _query_offerers_with_user_offerer() \
        .join(VenueSQLEntity, VenueSQLEntity.managingOffererId == Offerer.id) \
        .join(Offer) \
        .join(StockSQLEntity) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .filter(Offer.type != str(EventType.ACTIVATION))


def query_filter_offerer_by_user(query):
    return query.join(UserOfferer, (UserOfferer.userId == current_user.id) & (UserOfferer.offererId == Offerer.id)).filter_by(user=current_user)


def query_filter_offerer_is_not_validated(query):
    return _query_filter_user_offerer_by_validation_status(query, False)


def query_filter_offerer_is_validated(query):
    return _query_filter_user_offerer_by_validation_status(query, True)


def _query_filter_user_offerer_by_validation_status(query, is_validated: bool):
    if is_validated is True:
        return query.filter(Offerer.validationToken == None)
    else:
        return query.filter(Offerer.validationToken != None)
