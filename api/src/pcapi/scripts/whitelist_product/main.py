"""
Update gcuCompatibilityType to "WHITELISTED" for all products whose EAN exists in the ProductWhitelist table
"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.fraud.models import ProductWhitelist
from pcapi.core.offers.models import Product
from pcapi.models import db


logger = logging.getLogger(__name__)


def update_gcu_compatibility_whitelisted() -> None:
    logger.info("[START]")
    ean_list = db.session.query(ProductWhitelist.ean).all()
    ean_list = [ean for (ean,) in ean_list]

    if not ean_list:
        logger.info("No EAN in ProductWhitelist, nothing to update")
        return

    logger.info("%d ean retrieve", len(ean_list))

    logger.info("")
    db.session.query(Product).filter(Product.ean.in_(ean_list)).update(
        {Product.gcuCompatibilityType: "WHITELISTED"}, synchronize_session=False
    )
    logger.info("[END]")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    update_gcu_compatibility_whitelisted()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
