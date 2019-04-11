from models import Offer, Product
from repository import thing_queries, event_queries
from validation.events import check_user_can_create_activation_event
from validation.url import is_url_safe


def fill_offer_with_new_thing_data(payload: dict) -> Offer:
    product = Product(from_dict=payload)
    url = product.url
    if url:
        is_url_safe(url)
        product.isNational = True

    offer = _initialize_offer_from_thing(product)
    return offer


def fill_offer_with_new_event_data(payload: dict, user) -> Offer:
    product = Product(from_dict=payload)
    check_user_can_create_activation_event(user, product)
    offer = _initiaize_offer_from_event(product)
    return offer


def fill_offer_with_existing_thing_data(thing_id: str) -> Offer:
    thing = thing_queries.find_by_id(thing_id)
    offer = _initialize_offer_from_thing(thing)
    return offer


def fill_offer_with_existing_event_data(event_id: str) -> Offer:
    event = event_queries.find_by_id(event_id)
    offer = _initiaize_offer_from_event(event)
    return offer


def _initialize_offer_from_thing(thing):
    offer = Offer()
    offer.thing = thing
    offer.type = thing.type
    offer.name = thing.name
    offer.description = thing.description
    offer.url = thing.url
    offer.mediaUrls = thing.mediaUrls
    offer.isNational = thing.isNational
    offer.extraData = thing.extraData

def fill_offer_with_new_thing_data(thing_dict: str) -> Offer:
    product = Product()
    url = thing_dict.get('url')
    if url:
        is_url_safe(url)
        thing_dict['isNational'] = True
    product.populateFromDict(thing_dict)
    offer = Offer()
    offer.populateFromDict(thing_dict)
    offer.product = product
    return offer


def fill_offer_with_new_event_data(event_dict: dict, user) -> Offer:
    product = Product()
    product.populateFromDict(event_dict)
    check_user_can_create_activation_event(user, product)
    offer = Offer()
    offer.populateFromDict(event_dict)
    offer.product = product
    return offer


def fill_offer_with_existing_thing_data(thing_id: str, offer_data) -> Offer:
    product = thing_queries.find_by_id(thing_id)
    offer = Offer()
    offer.populateFromDict(offer_data)
    offer.product = product
    offer.type = product.type
    offer.name = product.name
    offer.description = product.description
    offer.url = product.url
    offer.mediaUrls = product.mediaUrls
    offer.isNational = product.isNational
    offer.extraData = product.extraData
    return offer


def _initiaize_offer_from_event(event_id) -> Offer:
    offer = Offer()
    product = event_queries.find_by_id(event_id)
    offer.product = product
    offer.type = product.type
    offer.name = product.name
    offer.description = product.description
    offer.mediaUrls = product.mediaUrls
    offer.conditions = product.conditions
    offer.ageMin = product.ageMin
    offer.ageMax = product.ageMax
    offer.accessibility = product.accessibility
    offer.durationMinutes = product.durationMinutes
    offer.isNational = product.isNational
    offer.extraData = product.extraData
    return offer
