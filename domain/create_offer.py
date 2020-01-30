from models import Offer, Product, User
from repository import product_queries
from validation.routes.events import check_user_can_create_activation_event
from validation.routes.url import is_url_safe


def initialize_offer_from_product_id(product_id: str) -> Offer:
    thing_product = product_queries.find_by_id(product_id)
    offer = initialize_offer_from_product(thing_product)
    return offer


def fill_offer_with_new_data(product_dict: str, user: User) -> Offer:
    product = Product()
    url = product_dict.get('url')
    if url:
        is_url_safe(url)
        product_dict['isNational'] = True
    product.populate_from_dict(product_dict)
    check_user_can_create_activation_event(user, product)
    offer = Offer()
    offer.populate_from_dict(product_dict)
    offer.product = product
    return offer


def initialize_offer_from_product(product) -> Offer:
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
