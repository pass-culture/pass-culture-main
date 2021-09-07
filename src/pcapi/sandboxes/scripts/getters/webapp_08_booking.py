from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.models import Mediation
from pcapi.core.users.models import User
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import Venue
from pcapi.repository.offer_queries import filter_bookable_stocks_query
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper
from pcapi.sandboxes.scripts.utils.helpers import get_offer_helper
from pcapi.utils.human_ids import humanize


def get_query_join_on_event(query):
    join_on_event = Offer.id == Stock.offerId
    query = query.join(Stock, join_on_event)
    return query


def get_query_join_on_thing(query):
    join_on_offer_id = Offer.id == Stock.offerId
    query = query.join(Stock, join_on_offer_id)
    return query


def get_non_free_offers_query_by_type():
    filter_not_free_price = Stock.price > 0
    filter_not_an_activation_offer = (Offer.subcategoryId != subcategories.ACTIVATION_EVENT.id) | (
        Offer.subcategoryId != subcategories.ACTIVATION_THING.id
    )

    query = Offer.query
    query = get_query_join_on_thing(query)
    query = filter_bookable_stocks_query(query)
    query = query.filter(filter_not_an_activation_offer).filter(filter_not_free_price)
    return query


def get_non_free_digital_offer():
    query = get_non_free_offers_query_by_type()
    offer = query.filter(Offer.url != None).first()
    return {"offer": get_offer_helper(offer)}


def get_non_free_thing_offer_with_active_mediation():
    query = get_non_free_offers_query_by_type()
    offer = (
        query.filter(Offer.url == None)
        .filter(Stock.beginningDatetime == None)
        .filter(Offer.mediations.any(Mediation.isActive == True))
        .join(Venue, Venue.id == Offer.venueId)
        .join(Offerer, Offerer.id == Venue.managingOffererId)
        .filter(Offerer.validationToken == None)
        .first()
    )

    if offer:
        return {
            "mediationId": [humanize(m.id) for m in offer.mediations if m.isActive][0],
            "offer": get_offer_helper(offer),
        }

    return {}


def get_non_free_event_offer():
    query = get_non_free_offers_query_by_type()
    offer = (
        query.filter(Offer.subcategoryId.in_(subcategories.EVENT_SUBCATEGORIES))
        .filter(Offer.mediations.any(Mediation.isActive == True))
        .join(Venue, Venue.id == Offer.venueId)
        .join(Offerer, Offerer.id == Venue.managingOffererId)
        .filter(Offerer.validationToken == None)
        .first()
    )

    if offer:
        return {
            "mediationId": [humanize(m.id) for m in offer.mediations if m.isActive][0],
            "offer": get_offer_helper(offer),
        }
    return {}


def get_existing_webapp_user_has_no_more_money():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("has-no-more-money"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}


def get_existing_webapp_user_can_book_thing_offer():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("93.has-confirmed-activation"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}


def get_existing_webapp_user_can_book_digital_offer():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("93.has-confirmed-activation"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}


def get_existing_webapp_user_can_book_event_offer():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("93.has-booked-some"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}


def get_existing_webapp_user_can_book_multidates():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("97.has-confirmed-activation"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}


def get_existing_webapp_user_reach_digital_limit():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("93.has-booked-some"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}


def get_existing_webapp_user_reach_physical_limit():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("93.has-booked-some"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}
