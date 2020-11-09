from flask import current_app as app

from pcapi.connectors import redis
from pcapi.domain.offers import is_from_allocine
from pcapi.models import Offer
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.validation.routes.offers import check_edition_for_allocine_offer_is_valid
from pcapi.validation.routes.offers import check_offer_is_editable


def update_an_offer(offer: Offer, modifications: dict) -> Offer:
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
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

    return offer


def _update_offer_for_allocine_offers(offer: Offer, modifications) -> Offer:
    modifications = _exclude_modifications_where_offer_value_wont_change(offer, modifications)

    check_edition_for_allocine_offer_is_valid(modifications)

    offer.populate_from_dict(modifications)
    offer.update_with_product_data(modifications)

    previously_updated_fields = set(offer.fieldsUpdated)
    updated_fields = set(modifications.keys())
    new_updated_fields = list(previously_updated_fields.union(updated_fields))

    offer.fieldsUpdated = new_updated_fields

    repository.save(offer)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

    return offer


def _exclude_modifications_where_offer_value_wont_change(offer: Offer, modifications):
    modifications_to_keep = dict()

    for (field, new_value) in modifications.items():
        if getattr(offer, field, None) != new_value:
            modifications_to_keep[field] = new_value

    return modifications_to_keep
