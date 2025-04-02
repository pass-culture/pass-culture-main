import argparse
from itertools import groupby
import logging

from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def remove_product_ean_duplicate(do_update: bool) -> None:
    products = (
        offers_models.Product.query.options(joinedload(offers_models.Product.offers))
        .filter(
            offers_models.Product.extraData["ean"].astext.is_not(None),
            offers_models.Product.extraData["ean"].astext != "",
        )
        .order_by(offers_models.Product.extraData["ean"].astext, offers_models.Product.id)
        .all()
    )

    products_group_by_ean = [list(g) for k, g in groupby(products, key=lambda p: p.extraData["ean"])]
    products_group_by_ean = [list_of_product for list_of_product in products_group_by_ean if len(list_of_product) > 1]
    logger.info("Found %d group of products with duplicate ean", len(products_group_by_ean))

    for products in products_group_by_ean:
        product_to_keep = products[0]
        products_to_remove = products[1:]
        logger.info(
            "[PREVIEW] For ean %s keep product id %d and delete %d products (id: %s)",
            product_to_keep.extraData["ean"],
            product_to_keep.id,
            len(products_to_remove),
            [p.id for p in products_to_remove],
        )
        for product in products_to_remove:
            logger.info(
                "[JOIN INFO] Product %d is linked to %d offers (id: %s)",
                product.id,
                len(product.offers),
                [o.id for o in product.offers],
            )
            for idx, offer in enumerate(product.offers):
                logger.info(
                    "[TRANSFER][%d/%d] offer: %d product %d to product %d",
                    idx + 1,
                    len(product.offers),
                    offer.id,
                    product.id,
                    product_to_keep.id,
                )
                offer.productId = product_to_keep.id

        do_commit(do_update)

        for product in products_to_remove:
            db.session.delete(product)
            logger.info("[DELETE] product %d", product.id)

        do_commit(do_update)


def do_commit(do_update: bool) -> None:
    if do_update:
        db.session.commit()
        print("Committed.")
    else:
        db.session.rollback()
        print("Dry run finished.")


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Remove product ean duplicate")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    if settings.IS_INTEGRATION:
        remove_product_ean_duplicate(args.not_dry)
    else:
        print("This script has been implemented to run in the integration environment only.")
