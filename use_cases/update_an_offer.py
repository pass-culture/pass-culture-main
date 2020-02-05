from pprint import pprint

from flask import current_app as app

from connectors import redis
from repository import repository
from domain.offers import is_from_allocine
from models import Offer
from validation.routes.offers import check_edition_for_allocine_offer_is_valid, check_offer_is_editable


def update_an_offer(offer: Offer, modifications: dict) -> Offer:

    if offer_name:
        check_offer_name_length_is_valid(offer_name)

    request_is_only_updating_isActive_status = _is_request_only_updating_isActive_status(modifications)

    if request_is_only_updating_isActive_status:
        return _update_offer_when_updating_isActive_field(offer, modifications)
    else:
        check_offer_is_editable(offer)

        if is_from_allocine(offer):
            offer = _update_offer_for_allocine_offers(offer, modifications)
        else:
            offer = _update_offer(offer, modifications)

        return offer


def _update_offer(offer: Offer, modifications) -> Offer:
    offer.populate_from_dict(modifications)
    offer.update_with_product_data(modifications)

    repository.save(offer)
    redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

    return offer


def _update_offer_for_allocine_offers(offer: Offer, modifications) -> Offer:
    check_edition_for_allocine_offer_is_valid(modifications)

    offer.populate_from_dict(modifications)
    offer.update_with_product_data(modifications)

    previously_updated_fields = set(offer.fieldsUpdated)
    updated_fields = set(modifications.keys())
    new_updated_fields = list(previously_updated_fields.union(updated_fields))

    offer.fieldsUpdated = new_updated_fields

    repository.save(offer)
    redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

    return offer


def _update_offer_when_updating_isActive_field(offer: Offer, modifications) -> Offer:
    offer.populate_from_dict(modifications)
    offer.update_with_product_data(modifications)

    repository.save(offer)
    redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

    return offer

def _is_request_only_updating_isActive_status(payload) -> bool:
    return 'isActive' in payload and len(payload) == 1
