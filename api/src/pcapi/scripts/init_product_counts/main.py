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


def chronicles_count_query() -> sa.sql.expression.Select:
    return sa.select(
        ProductChronicle.productId.label("product_id"), sa.func.count(ProductChronicle.productId).label("total")
    ).group_by(ProductChronicle.productId)


def headlines_count_query() -> sa.sql.expression.Select:
    return (
        sa.select(Offer.productId.label("product_id"), sa.func.count(Offer.productId).label("total"))
        .select_from(HeadlineOffer)
        .join(Offer, HeadlineOffer.offerId == Offer.id)
        .where(Offer.productId.is_not(None))
        .group_by(Offer.productId)
    )


def likes_count_query() -> sa.sql.expression.Select:
    return (
        sa.select(Reaction.productId.label("product_id"), sa.func.count(Reaction.productId).label("total"))
        .where(Reaction.reactionType == ReactionTypeEnum.LIKE, Reaction.productId.is_not(None))
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


def main(not_dry: bool) -> None:
    update_product_count(chronicles_count_query(), "chroniclesCount", not_dry)
    update_product_count(headlines_count_query(), "headlinesCount", not_dry)
    update_product_count(likes_count_query(), "likesCount", not_dry)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
