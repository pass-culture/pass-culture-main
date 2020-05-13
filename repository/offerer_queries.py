from datetime import datetime

from flask_login import current_user
from sqlalchemy import or_

from domain.keywords import create_filter_matching_all_keywords_in_any_model, \
    create_get_filter_matching_ts_query_in_any_model
from models import Offerer, Venue, Offer, UserOfferer, UserSQLEntity, StockSQLEntity, Recommendation, ThingType, EventType
from models import RightsType
from models.db import db

get_filter_matching_ts_query_for_offerer = create_get_filter_matching_ts_query_in_any_model(
    Offerer,
    Venue
)


def count_offerer() -> int:
    return _query_offerers_with_user_offerer().count()


def count_offerer_by_departement(departement_code: str) -> int:
    return _query_offerers_with_user_offerer() \
        .join(Venue, Venue.managingOffererId == Offerer.id) \
        .filter(Venue.departementCode == departement_code) \
        .count()


def count_offerer_with_stock() -> int:
    return _query_offerers_with_stock().count()


def count_offerer_with_stock_by_departement(departement_code: str) -> int:
    return _query_offerers_with_stock() \
        .filter(Venue.departementCode == departement_code) \
        .count()


def find_by_id(id):
    return Offerer.query.filter_by(id=id).first()


def find_by_siren(siren):
    return Offerer.query.filter_by(siren=siren).first()


def get_by_offer_id(offer_id):
    return Offerer.query.join(Venue).join(Offer).filter_by(id=offer_id).first()


def find_new_offerer_user_email(offerer_id):
    return UserOfferer.query \
        .filter_by(offererId=offerer_id) \
        .join(UserSQLEntity) \
        .with_entities(UserSQLEntity.email) \
        .first()[0]


def find_first_by_user_offerer_id(user_offerer_id):
    return Offerer.query.join(UserOfferer).filter_by(id=user_offerer_id).first()


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
    return query.filter(Offerer.managedVenues.any(Venue.isVirtual == False))


def keep_offerers_with_no_physical_venue(query):
    is_not_virtual = Venue.isVirtual == False
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
        .join(Venue, Venue.managingOffererId == Offerer.id) \
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
