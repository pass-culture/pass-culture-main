"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43477/script_add_integration_movies \
  -f NAMESPACE=reindex_movies \
  -f SCRIPT_ARGUMENTS="";

"""

import logging
import typing

import sqlalchemy as sa

from pcapi.core import search
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.models import db


logger = logging.getLogger(__name__)


def fetch_product_ids_with_an_allocine_id() -> list[int]:
    # not meant to run inside a production or production-like environment
    # there should not be many movie products
    return [
        row[0]
        for row in db.session.query(Product)
        .filter(sa.not_(Product.extraData.op("->")("allocineId").is_(None)))
        .limit(100)
        .with_entities(Product.id)
    ]


def fetch_offer_ids_from_their_products(product_ids: typing.Collection[int]) -> list[int]:
    return [row[0] for row in db.session.query(Offer).filter(Offer.productId.in_(product_ids)).with_entities(Offer.id)]


def main() -> None:
    product_ids = fetch_product_ids_with_an_allocine_id()
    logger.info("Found %d products with an allocine id: %s", len(product_ids), str(product_ids))

    offer_ids = fetch_offer_ids_from_their_products(product_ids)
    logger.info("Found %d related offers", len(product_ids))

    search.async_index_offer_ids(offer_ids, reason=search.models.IndexationReason.OFFER_MANUAL_REINDEXATION)
    logger.info("Async reindex triggered. Done.")


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    main()
