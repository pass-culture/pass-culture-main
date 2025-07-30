import argparse
import logging

from sqlalchemy.orm import joinedload

from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


PRODUCT_IDS = [
    460410,
    924892,
    924980,
    1030343,
    1316900,
    1686376,
    165593,
    1082566,
    1686360,
    1686362,
    1686365,
    1686366,
    1686367,
    1686370,
    1686375,
    1365842,
    1686361,
    1590151,
    1590908,
    5605323,
    698196,
]


def get_products_to_delete() -> list[offers_models.Product]:
    query = offers_models.Product.query.filter(
        offers_models.Product.id.in_(PRODUCT_IDS),
    ).options(joinedload(offers_models.Product.offers))
    return query.all()


def execute_request(dry_run: bool = True) -> None:
    for product in get_products_to_delete():
        if product.offers:
            raise ValueError()
    offers_models.Product.query.filter(offers_models.Product.id.in_(PRODUCT_IDS)).delete()
    if dry_run:
        logger.info("Dry run: would delete product ids: %s", PRODUCT_IDS)
        db.session.rollback()
    else:
        logger.info("Deleting product ids: %s", PRODUCT_IDS)
        db.session.commit()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()
    parser = argparse.ArgumentParser(
        description="Remove useless key from offer jsonData if offer is linked to a product"
    )
    parser.add_argument("--dry-run", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()
    execute_request(args.dry_run)
