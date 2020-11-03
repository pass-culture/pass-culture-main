from flask import current_app as app
from typing import Optional

from pcapi.connectors import redis
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository.offer_queries import update_offers_is_active_status, get_all_offers_id_by_filters
from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters


def update_all_offers_active_status(user_id: int,
                                    user_is_admin: bool,
                                    is_active: bool,
                                    offerer_id: Optional[Identifier] = None,
                                    status_filters: OffersStatusFilters = OffersStatusFilters(),
                                    venue_id: Optional[Identifier] = None,
                                    name_keywords: Optional[str] = None):
    offers_id = get_all_offers_id_by_filters(user_id, user_is_admin, offerer_id, status_filters, venue_id, name_keywords)

    update_offers_active_status(offers_id, is_active)


def update_offers_active_status(offers_id: [int], is_active_status: bool):
    update_offers_is_active_status(offers_id, is_active_status)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        for offer_id in offers_id:
            redis.add_offer_id(client=app.redis_client, offer_id=offer_id)
