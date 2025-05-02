"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35946-script-initialize-product-counts/api/src/pcapi/scripts/init_product_counts/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.chronicles.models import ProductChronicle
from pcapi.core.offers.models import HeadlineOffer
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.reactions.models import Reaction
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.models import db


logger = logging.getLogger(__name__)


def chronicles_count_query(start: int, end: int) -> sa.sql.expression.Select:
    return (
        sa.select(
            ProductChronicle.productId.label("product_id"), sa.func.count(ProductChronicle.productId).label("total")
        )
        .where(ProductChronicle.productId >= start, ProductChronicle.productId < end)
        .group_by(ProductChronicle.productId)
    )


def headlines_count_query(start: int, end: int) -> sa.sql.expression.Select:
    return (
        sa.select(Offer.productId.label("product_id"), sa.func.count(Offer.productId).label("total"))
        .select_from(HeadlineOffer)
        .join(Offer, HeadlineOffer.offerId == Offer.id)
        .where(Offer.productId >= start, Offer.productId < end)
        .group_by(Offer.productId)
    )


def likes_count_query(start: int, end: int) -> sa.sql.expression.Select:
    return (
        sa.select(Reaction.productId.label("product_id"), sa.func.count(Reaction.productId).label("total"))
        .where(Reaction.reactionType == ReactionTypeEnum.LIKE)
        .where(Reaction.productId >= start, Reaction.productId < end)
        .group_by(Reaction.productId)
    )


def update_product_count(count_query: sa.sql.expression.Select, col_name: str, not_dry: bool) -> None:
    subquery = count_query.subquery()
    update_query = (
        sa.update(Product)
        .where(Product.id == subquery.c.product_id)
        .values({col_name: subquery.c.total})
        .execution_options(synchronize_session=False)
    )
    db.session.execute(update_query)

    if not_dry:
        db.session.commit()
        logger.info("Column %s updated", col_name)
    else:
        logger.info("Dry run, rollback")
        db.session.rollback()


def main(batch_size: int, not_dry: bool) -> None:
    start = 0
    product_max_id = db.session.execute(sa.select(sa.func.max(Product.id))).scalar()
    while start < product_max_id:
        update_product_count(chronicles_count_query(start, start + batch_size), "chroniclesCount", not_dry)
        update_product_count(headlines_count_query(start, start + batch_size), "headlinesCount", not_dry)
        update_product_count(likes_count_query(start, start + batch_size), "likesCount", not_dry)

        logger.info("Updated products from id %d to %d", start, min(start + batch_size, product_max_id))
        start += batch_size


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--batch-size", type=int, default=1_000)
    args = parser.parse_args()

    main(args.batch_size, not_dry=args.not_dry)
