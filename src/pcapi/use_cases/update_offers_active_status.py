from flask import current_app as app

from pcapi.connectors import redis
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository.offer_queries import update_offers_is_active_status


def update_offers_active_status(offers_id: [int], is_active_status: bool):
    update_offers_is_active_status(offers_id, is_active_status)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        for offer_id in offers_id:
            redis.add_offer_id(client=app.redis_client, offer_id=offer_id)

