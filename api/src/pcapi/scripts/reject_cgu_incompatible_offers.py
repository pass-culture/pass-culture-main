import argparse
from datetime import datetime
import logging
import os

from sqlalchemy.orm import Query
from sqlalchemy.orm import load_only


LOGGER = logging.getLogger(__name__)


def get_ineligible_product_ids() -> Query:
    """returns ineligible products with an ISBN"""
    return Product.query.filter(
        Product.isGcuCompatible.is_(False),
        Product.extraData.op("->")("isbn").is_not(None),
    ).options(load_only("id"))


def get_ineligible_offers(product_id: int) -> Query:
    return Offer.query.filter(
        Offer.productId == product_id,
        Offer.validation != OfferValidationStatus.REJECTED,
    )


def reject_offers(product_id: int, dry_run: bool = True) -> int:
    start = datetime.utcnow()
    offers = get_ineligible_offers(product_id)
    offers_count = offers.count()

    if dry_run:
        LOGGER.info("%s offers related to product %s would have been rejected", offers_count, product_id)

    else:
        offers.update(
            values={
                "validation": OfferValidationStatus.REJECTED,
                "lastValidationDate": datetime.utcnow(),
                "lastValidationType": OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
            },
            synchronize_session="fetch",
        )
        db.session.commit()
        LOGGER.info(
            "rejected %s offers related to product %s in %s", offers_count, product_id, datetime.utcnow() - start
        )

    return offers_count


def main(dry_run: bool = True) -> None:
    try:
        with app.app_context():
            start = datetime.utcnow()
            LOGGER.info("starting rejection of non GCU compatible offers")
            rejected_offers = 0
            processed_products = 0

            product_ids = get_ineligible_product_ids().all()
            LOGGER.info("%s non GCU compliant products found", len(product_ids))

            for product in product_ids:
                rejected_offers += reject_offers(product.id, dry_run=dry_run)
                processed_products += 1

    except KeyboardInterrupt:
        LOGGER.info("keybord interrupted")

    LOGGER.info(
        "report: %s offers rejected from %s products in %s",
        rejected_offers,
        processed_products,
        datetime.utcnow() - start,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="format users phone number in DB")
    parser.add_argument("--not-dry", action="store_true", help="used to really process the formatting")
    parser.add_argument("--local", action="store_true", help="used to run on local machine (for tests)")
    args = parser.parse_args()

    if args.local:
        os.environ["CORS_ALLOWED_ORIGINS"] = ""
        os.environ["CORS_ALLOWED_ORIGINS_BACKOFFICE"] = ""
        os.environ["CORS_ALLOWED_ORIGINS_NATIVE"] = ""
        os.environ["CORS_ALLOWED_ORIGINS_ADAGE_IFRAME"] = ""
        os.environ["DATABASE_URL"] = "postgresql://pass_culture:pass_culture@localhost:5434/pass_culture"

    from pcapi.core.offers.models import Offer
    from pcapi.core.offers.models import Product
    from pcapi.flask_app import app
    from pcapi.flask_app import db
    from pcapi.models.offer_mixin import OfferValidationStatus
    from pcapi.models.offer_mixin import OfferValidationType

    main(
        dry_run=not args.not_dry,
    )
