from models import Offer, Product, User
from repository import thing_queries
from validation.events import check_user_can_create_activation_event
from validation.url import is_url_safe


def fill_offer_with_existing_data(product_id: str) -> Offer:
    thing = thing_queries.find_by_id(product_id)
    offer = _initialize_offer_from_thing(thing)
    return offer


def fill_offer_with_new_data(thing_dict: str, user: User) -> Offer:
    product = Product()
    url = thing_dict.get('url')
    if url:
        is_url_safe(url)
        thing_dict['isNational'] = True
    product.populateFromDict(thing_dict)
    check_user_can_create_activation_event(user, product)
    offer = Offer()
    offer.populateFromDict(thing_dict)
    offer.product = product
    return offer


def _initialize_offer_from_thing(product):
    offer = Offer()
    offer.product = product
    offer.type = product.type
    offer.name = product.name
    offer.description = product.description
    offer.url = product.url
    offer.mediaUrls = product.mediaUrls
    offer.conditions = product.conditions
    offer.ageMin = product.ageMin
    offer.ageMax = product.ageMax
    offer.durationMinutes = product.durationMinutes
    offer.isNational = product.isNational
    offer.extraData = product.extraData
    return offer
