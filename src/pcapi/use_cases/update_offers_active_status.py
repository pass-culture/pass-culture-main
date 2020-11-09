from typing import Optional

from flask import current_app as app

from pcapi.connectors import redis
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository.offer_queries import get_all_offers_id_by_filters
from pcapi.repository.offer_queries import update_offers_is_active_status


def update_all_offers_active_status(
    user_id: int,
    user_is_admin: bool,
    is_active: bool,
    offerer_id: Optional[int] = None,
    status: Optional[str] = None,
    venue_id: Optional[int] = None,
    type_id: Optional[str] = None,
    name_keywords: Optional[str] = None,
    creation_mode: Optional[str] = None,
):
    offers_id = get_all_offers_id_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        type_id=type_id,
        name_keywords=name_keywords,
        creation_mode=creation_mode
    )

    update_offers_active_status(offers_id, is_active)


def update_offers_active_status(offers_id: [int], is_active_status: bool):
    update_offers_is_active_status(offers_id, is_active_status)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        for offer_id in offers_id:
            redis.add_offer_id(client=app.redis_client, offer_id=offer_id)
