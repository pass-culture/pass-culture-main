from flask import current_app as app

from pcapi.connectors import redis
from pcapi.models import OfferSQLEntity
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository, feature_queries


def update_an_offer_active_status(offer: OfferSQLEntity, is_active_status: bool):
    activation_data = {'isActive': is_active_status}
    offer.populate_from_dict(activation_data)
    offer.update_with_product_data(activation_data)

    repository.save(offer)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

