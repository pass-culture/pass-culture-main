from typing import List

from flask import current_app as app

from pcapi.connectors import redis
from pcapi.models import Offer
from pcapi.repository import repository


def deactivate_inappropriate_offers(offer_ids: List[int]):
    offers = Offer.query.filter(Offer.id.in_(offer_ids)).all()
    for o in offers:
        o.isActive = False
        o.product.isGcuCompatible = False
    repository.save(*offers)
    for o in offers:
        redis.add_offer_id(client=app.redis_client, offer_id=o.id)
