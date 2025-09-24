import logging

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

from pcapi.core.offers import models as offers_models
from pcapi.core.products import models as products_models
from pcapi.core.reactions import models as reactions_models
from pcapi.models import db
from pcapi.utils.decorators import retry


logger = logging.getLogger(__name__)


def get_product_reaction_count_subquery() -> sa.sql.selectable.ScalarSelect:
    return (
        sa.select(sa.func.count(reactions_models.Reaction.id))
        .select_from(reactions_models.Reaction)
        .where(reactions_models.Reaction.productId == products_models.Product.id)
        .where(reactions_models.Reaction.reactionType == reactions_models.ReactionTypeEnum.LIKE)
        .correlate(products_models.Product)
        .scalar_subquery()
    )


def get_movie_products_matching_allocine_id_or_film_visa(
    allocine_id: str | None,
    visa: str | None,
) -> list[products_models.Product]:
    """
    One of the two parameters must be defined.

    As there are unique indexes on `extraData["allocineId"]` and `extraData["visa"]`,
    this function can return at most 2 products.
    """
    filters = []

    if not allocine_id and not visa:
        raise ValueError("`allocine_id` or `visa` must be defined")

    if allocine_id:
        filters.append((products_models.Product.extraData["allocineId"] == str(allocine_id)))

    if visa:
        filters.append((products_models.Product.extraData["visa"].astext == visa))

    return db.session.query(products_models.Product).filter(sa.or_(*filters)).all()


def _log_deletion_error(_to_keep: products_models.Product, to_delete: products_models.Product) -> None:
    logger.info("Failed to delete product %d", to_delete.id)


@retry(
    exception=sa_exc.IntegrityError,
    exception_handler=_log_deletion_error,
    logger=logger,
    max_attempts=3,
)
def merge_products(to_keep: products_models.Product, to_delete: products_models.Product) -> products_models.Product:
    # It has already happened that an offer is created by another SQL session
    # in between the transfer of the offers and the product deletion.
    # This causes the product deletion to fail with an IntegrityError
    # `update or delete on table "product" violates foreign key constraint "offer_productId_fkey" on table "offer"`
    # To fix this race condition requires to force taking an Access Exclusive lock on the product to delete.
    # Because this situation is rare, we use a `retry` instead. That should be sufficient.

    db.session.query(offers_models.Offer).filter(offers_models.Offer.productId == to_delete.id).update(
        {"productId": to_keep.id}
    )
    db.session.query(reactions_models.Reaction).filter(reactions_models.Reaction.productId == to_delete.id).update(
        {"productId": to_keep.id}
    )
    db.session.delete(to_delete)
    db.session.flush()

    return to_keep
