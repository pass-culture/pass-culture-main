import logging

from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy import or_

from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.repository import transaction


LOGGER = logging.getLogger(__name__)


CHUNK_SIZE = 1000

PRODUCTS_TO_DELETE_QUERY_FILTERS = offers_models.Product.query.with_entities(offers_models.Product.id).filter(
    offers_models.Product.extraData["ean"].astext.is_not(None),
    or_(
        offers_models.Product.owningOffererId.is_not(None),
        and_(
            offers_models.Product.owningOffererId.is_(None),
            offers_models.Product.idAtProviders.is_(None),
            offers_models.Product.lastProviderId.is_(None),
        ),
    ),
)

# In case we wan to delete all producrs with ean and no id at provider or last provider id
# PRODUCTS_TO_DELETE_QUERY = (
#     offers_models.Product.query.with_entities(offers_models.Product.id)
#     .filter(
#         offers_models.Product.extraData["ean"].astext.is_not(None),
#         offers_models.Product.idAtProviders.is_(None),
#         offers_models.Product.lastProviderId.is_(None),
#     )

MAX_PRODUCT_ID = PRODUCTS_TO_DELETE_QUERY_FILTERS.order_by(desc(offers_models.Product.id)).limit(1).scalar()


def execute_request(start_id: int, dry_run: bool = True):
    while start_id < MAX_PRODUCT_ID:
        with transaction():
            products_to_delete_query = (
                PRODUCTS_TO_DELETE_QUERY_FILTERS.filter(offers_models.Product.id >= start_id)
                .order_by(offers_models.Product.id)
                .limit(CHUNK_SIZE)
            )

            products_ids_to_delete = [p.id for p in products_to_delete_query.all()]
            for product_id in products_ids_to_delete:
                LOGGER.info("Product %s would have been deleted", product_id)

            offers = offers_models.Offer.query.filter(offers_models.Offer.productId.in_(products_ids_to_delete)).all()
            for offer in offers:
                offer.productId = None
                offer.is_soft_deleted = True
                LOGGER.info("Offer %s would have been modified", offer.id)

            db.session.add_all(offers)
            offers_models.Product.query.filter(
                offers_models.Product.id.in_(products_to_delete_query.subquery())
            ).delete(synchronize_session=False)

            if dry_run:
                db.session.rollback()
            else:
                db.session.commit()
            start_id = products_ids_to_delete[-1] + 1
