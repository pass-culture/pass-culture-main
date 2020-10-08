from flask import current_app as app

from connectors import redis
from models import OfferSQLEntity
from models.feature import FeatureToggle
from repository import repository, feature_queries


def activate_an_offer(offer: OfferSQLEntity):
    activation_data = {'isActive': True}
    offer.populate_from_dict(activation_data)
    offer.update_with_product_data(activation_data)

    repository.save(offer)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

