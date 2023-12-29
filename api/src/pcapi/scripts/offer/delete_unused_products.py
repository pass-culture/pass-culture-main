import logging

from sqlalchemy.orm import joinedload

from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)


CHUNK_SIZE = 500


def get_products_to_delete(from_id: int):
    query = (
        offers_models.Product.query.filter(
            offers_models.Product.owningOffererId.is_not(None),
            offers_models.Product.idAtProviders.is_(None),
            offers_models.Product.lastProviderId.is_(None),
            offers_models.Product.id.between(from_id, from_id + CHUNK_SIZE),
        )
        # For products with an owningOfferer this is a 1-1 relationship
        .options(joinedload(offers_models.Product.offers))
    )
    logger.info("Batch from id : %s", from_id)
    for product in query:
        yield product


def execute_request(start_id: int, stop_id: int, dry_run: bool = True):
    for id in range(start_id, stop_id, CHUNK_SIZE):
        with transaction():
            product_to_delete = get_products_to_delete(id)
            products_id_to_delete = []
            for product in product_to_delete:
                for offer in product.offers:
                    offer.productId = None

                logger.info("Updating offers ids : %s", [offer.id for offer in product.offers])
                db.session.add_all(product.offers)
                products_id_to_delete.append(product.id)
            logger.info("Deleting products ids : %s", products_id_to_delete)
            offers_models.Product.query.filter(offers_models.Product.id.in_(products_id_to_delete)).delete(
                synchronize_session=False
            )
            if dry_run:
                db.session.rollback()
