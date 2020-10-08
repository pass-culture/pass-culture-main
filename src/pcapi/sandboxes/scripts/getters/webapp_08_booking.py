from pcapi.models import StockSQLEntity, EventType, ThingType, MediationSQLEntity, OfferSQLEntity, VenueSQLEntity, Offerer
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository.offer_queries import _filter_bookable_stocks_for_discovery
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper, get_offer_helper
from pcapi.utils.human_ids import humanize


def get_query_join_on_event(query):
    join_on_event = (OfferSQLEntity.id == StockSQLEntity.offerId)
    query = query.join(StockSQLEntity, join_on_event)
    return query


def get_query_join_on_thing(query):
    join_on_offer_id = (OfferSQLEntity.id == StockSQLEntity.offerId)
    query = query.join(StockSQLEntity, join_on_offer_id)
    return query


def get_non_free_offers_query_by_type():
    filter_not_free_price = (StockSQLEntity.price > 0)
    filter_not_an_activation_offer = \
        (OfferSQLEntity.type != str(EventType.ACTIVATION)) \
        | (OfferSQLEntity.type != str(ThingType.ACTIVATION))

    query = OfferSQLEntity.query
    query = get_query_join_on_thing(query)
    query = _filter_bookable_stocks_for_discovery(query)
    query = query \
        .filter(filter_not_an_activation_offer) \
        .filter(filter_not_free_price)
    return query


def get_non_free_digital_offer():
    query = get_non_free_offers_query_by_type()
    offer = query \
        .filter(OfferSQLEntity.url != None) \
        .first()
    return {
        "offer": get_offer_helper(offer)
    }


def get_non_free_thing_offer_with_active_mediation():
    query = get_non_free_offers_query_by_type()
    offer = query \
        .filter(OfferSQLEntity.url == None) \
        .filter(StockSQLEntity.beginningDatetime == None) \
        .filter(OfferSQLEntity.mediations.any(MediationSQLEntity.isActive == True)) \
        .join(VenueSQLEntity, VenueSQLEntity.id == OfferSQLEntity.venueId) \
        .join(Offerer, Offerer.id == VenueSQLEntity.managingOffererId) \
        .filter(Offerer.validationToken == None) \
        .first()

    if offer:
        return {
            "mediationId": [humanize(m.id) for m in offer.mediations if m.isActive][0],
            "offer": get_offer_helper(offer)
        }

    return {}


def get_non_free_event_offer():
    query = get_non_free_offers_query_by_type()
    offer = query \
        .filter(OfferSQLEntity.type.in_([str(event_type) for event_type in EventType])) \
        .filter(OfferSQLEntity.mediations.any(MediationSQLEntity.isActive == True)) \
        .join(VenueSQLEntity, VenueSQLEntity.id == OfferSQLEntity.venueId) \
        .join(Offerer, Offerer.id == VenueSQLEntity.managingOffererId) \
        .filter(Offerer.validationToken == None) \
        .first()

    if offer:
        return {
            "mediationId": [humanize(m.id) for m in offer.mediations if m.isActive][0],
            "offer": get_offer_helper(offer)
        }
    return {}


def get_existing_webapp_user_has_no_more_money():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('has-no-more-money'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_webapp_user_can_book_thing_offer():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('93.has-confirmed-activation'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_webapp_user_can_book_digital_offer():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('93.has-confirmed-activation'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_webapp_user_can_book_event_offer():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_webapp_user_can_book_multidates():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('97.has-confirmed-activation'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_webapp_user_reach_digital_limit():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_webapp_user_reach_physical_limit():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }
