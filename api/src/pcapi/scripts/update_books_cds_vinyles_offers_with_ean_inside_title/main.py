from dataclasses import dataclass
import logging
from typing import Collection
from typing import Generator

import sqlalchemy as sa

from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Product
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)

# Mandatory since this module uses atomic() which needs an application context.
app.app_context().push()


LEGIT_BOOKS_CDS_VINYLES_WITH_EAN_INSIDE_TITLE_QUERY = """
    SELECT
        sub.offer_id,
        sub.ean,
        product.id as product_id
    FROM (
        SELECT
            offer.id as offer_id,
            substring("name" similar '%#"[[:digit:]]{13}#"%' escape '#') as ean
        FROM
            offer
        WHERE
            -- offer with ean inside title
            offer."name" similar to '%\\d{13}%'
            AND offer.id >= :lower_bound
            AND offer.id < :upper_bound
            -- not all subcategories can have EAN
            AND offer."subcategoryId" in (
                'LIVRE_PAPIER',
                'SUPPORT_PHYSIQUE_MUSIQUE_CD',
                'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE'
            )
            AND offer.validation != 'REJECTED'
            AND offer."isActive" is true
    ) sub
    LEFT JOIN
        product on (
            product.id = sub.offer_id
            OR product."jsonData"->>'ean'::text = sub.ean
        )
    WHERE
        -- offer is known and gcu incompatible
        product.id IS NOT NULL
        AND product."gcuCompatibilityType" = 'COMPATIBLE'
"""


@dataclass(frozen=True)
class OfferRow:
    offer_id: int
    ean: str
    product_id: int


def update_offers_with_ean_inside_title(
    min_id: int | None = None, max_id: int | None = None, batch_size: int | None = None, commit_size: int | None = None
) -> None:
    if not commit_size:
        commit_size = 250

    rows_iterator = get_offers_with_ean_inside_title(min_id=min_id, max_id=max_id, batch_size=batch_size)
    for idx, chunk in enumerate(get_chunks(rows_iterator, commit_size)):
        logger.info("start loop #%d with %d ids...", idx, len(chunk))
        update_offers(chunk)


def get_offers_with_ean_inside_title(
    min_id: int | None = None, max_id: int | None = None, batch_size: int | None = None
) -> Generator[OfferRow, None, None]:
    query = sa.text(LEGIT_BOOKS_CDS_VINYLES_WITH_EAN_INSIDE_TITLE_QUERY)

    if not min_id:
        min_id = list(db.session.execute("SELECT min(id) FROM offer"))[0][0]

    if not max_id:
        max_id = list(db.session.execute("SELECT max(id) FROM offer"))[0][0]

    assert min_id is not None
    assert max_id is not None

    if not batch_size:
        batch_size = 10_000 if max_id > 100_000 else max((min_id - max_id) // 10, 2)

    assert batch_size is not None

    for upper_bound in reversed(range(min_id, max_id + batch_size + 1, batch_size)):
        query_params = {"upper_bound": upper_bound, "lower_bound": upper_bound - batch_size}
        logger.info("yield rows from %d to %d", upper_bound - batch_size, upper_bound)
        for row in db.session.execute(query, query_params):
            yield OfferRow(offer_id=row[0], ean=row[1], product_id=row[2])


def _update_one_offer(offer: Offer, ean: str, product: Product) -> None:
    # Start by updating current offer field from product
    offer.name = product.name
    offer.extraData = product.extraData
    offer.product = product

    # Find out if there are other active offers from the same venue
    offers_from_same_venue_with_same_ean = (
        Offer.query.join(Offer.venue)
        .filter(
            Venue.id == offer.venueId,
            sa.or_(Offer.extraData["ean"].astext == ean, Offer.ean == ean),
            Offer.isActive == True,
        )
        .options(sa.orm.load_only(Offer.id, Offer.name, Offer.extraData, Offer.isActive, Offer.dateCreated))
        .all()
    )

    # Find the most recent one, activate it and deactivate the others
    _offers = sorted(offers_from_same_venue_with_same_ean + [offer], key=lambda o: o.dateCreated)

    if not _offers:
        offer.isActive = True
        return

    most_recent_one = _offers.pop()
    most_recent_one.isActive = True

    for _offer in _offers:
        _offer.isActive = False

    logger.info(
        (
            "[%d update] Found %d offers with same EAN, "
            "%d is the most recent one (is active) others have been deactivated"
        ),
        offer.id,
        len(_offers) + 1,
        most_recent_one.id,
    )


@atomic()
def update_offers(offer_rows: Collection[OfferRow]) -> None:
    """Update offers from their matching product data.

    If a venue has more than one active offer with the same EAN, only
    the last one should be left active.
    """

    offer_ids = {row.offer_id for row in offer_rows}
    offers_query = Offer.query.filter(
        Offer.id.in_(offer_ids),
        Offer.status != OfferValidationStatus.REJECTED.value,
    ).options(sa.orm.joinedload(Offer.product).load_only(Product.extraData, Product.name))

    product_ids = {row.product_id for row in offer_rows}
    products_query = Product.query.filter(Product.id.in_(product_ids)).options(
        sa.orm.load_only(Product.extraData, Product.name)
    )

    offer_ean_mapping = {row.offer_id: row.ean for row in offer_rows}
    product_mapping = {product.id: product for product in products_query}
    offer_product_mapping = {row.offer_id: product_mapping[row.product_id] for row in offer_rows}

    for offer in offers_query:
        _update_one_offer(offer, offer_ean_mapping[offer.id], offer_product_mapping[offer.id])

    logger.info("%d offers updated, from id %d to %d", len(offer_ids), min(offer_ids), max(offer_ids))


if __name__ == "__main__":
    import sys

    min_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    max_id_arg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    batch_size_arg = int(sys.argv[3]) if len(sys.argv) > 3 else None
    commit_size_arg = int(sys.argv[4]) if len(sys.argv) > 4 else None

    update_offers_with_ean_inside_title(min_id_arg, max_id_arg, batch_size_arg, commit_size_arg)
