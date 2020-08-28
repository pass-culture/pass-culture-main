from flask import current_app as app

from connectors import redis
from models import OfferSQLEntity
from repository import repository


def deactivate_inappropriate_offers():
    offers = OfferSQLEntity.query.filter(OfferSQLEntity.description.ilike('%hentaï%')).all()
    for o in offers:
        o.isActive = False
        o.product.isGcuCompatible = False
    repository.save(*offers)
    for o in offers:
        redis.add_offer_id(client=app.redis_client, offer_id=o.id)
