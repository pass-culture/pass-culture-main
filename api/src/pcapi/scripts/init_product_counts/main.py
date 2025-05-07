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


def compute_chronicles_count(not_dry: bool) -> None:
    chronicles_count_cte = (
        sa.select(
            ProductChronicle.productId.label("productId"), sa.func.count(ProductChronicle.productId).label("total")
        )
        .group_by(ProductChronicle.productId)
        .cte()
    )
    update_products(chronicles_count_cte, "chroniclesCount", not_dry)


def compute_headlines_count(not_dry: bool) -> None:
    headlines_count_cte = (
        sa.select(Offer.productId.label("productId"), sa.func.count(Offer.productId).label("total"))
        .select_from(HeadlineOffer)
        .join(Offer, HeadlineOffer.offerId == Offer.id)
        .where(Offer.productId.is_not(None))
        .group_by(Offer.productId)
        .cte()
    )
    update_products(headlines_count_cte, "headlinesCount", not_dry)


def compute_likes_count(not_dry: bool) -> None:
    likes_count_cte = (
        sa.select(Reaction.productId.label("productId"), sa.func.count(Reaction.productId).label("total"))
        .where(Reaction.reactionType == ReactionTypeEnum.LIKE, Reaction.productId.is_not(None))
        .group_by(Reaction.productId)
        .cte()
    )
    update_products(likes_count_cte, "likesCount", not_dry)


def update_products(count_cte: sa.sql.expression.CTE, col_name: str, not_dry: bool) -> None:
    update_query = (
        sa.update(Product)
        .where(Product.id == count_cte.c.productId)
        .values({col_name: count_cte.c.total})
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
    compute_chronicles_count(not_dry)
    compute_headlines_count(not_dry)
    compute_likes_count(not_dry)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
