import logging
from typing import Generator

import sqlalchemy as sa

from pcapi.flask_app import app
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)

app.app_context().push()


OFFERS_WITH_TWO_DIFFERENT_EANS_QUERY = """
    SELECT
        offer.id as offer_id
    FROM
        offer
    LEFT JOIN
        product ON product.ean = offer."jsonData"->>'ean'::text
    WHERE
        product.id IS NOT NULL
        AND product."gcuCompatibilityType" = 'COMPATIBLE'
        -- offer with two different EANs
        AND offer.ean != offer."jsonData"->>'ean'::text
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
"""

OFFERS_WITH_TWO_DIFFERENT_EANS_UPDATE_QUERY = """
    UPDATE offer
    SET ean = "jsonData"->>'ean'
    WHERE id = ANY(:offer_ids)
"""


def get_offers_with_two_different_eans(
    min_id: int | None = None, max_id: int | None = None, batch_size: int | None = None
) -> Generator[int, None, None]:
    query = sa.text(OFFERS_WITH_TWO_DIFFERENT_EANS_QUERY)

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
            yield row[0]


def fix_offers_with_two_different_eans(
    min_id: int | None = None, max_id: int | None = None, batch_size: int | None = None, commit_size: int | None = None
) -> None:
    if not commit_size:
        commit_size = 250

    query = sa.text(OFFERS_WITH_TWO_DIFFERENT_EANS_UPDATE_QUERY)

    rows_iterator = get_offers_with_two_different_eans(min_id=min_id, max_id=max_id, batch_size=batch_size)
    for idx, chunk in enumerate(get_chunks(rows_iterator, commit_size)):
        logger.info("start loop #%d with %d ids...", idx, len(chunk))

        db.session.execute(query, {"offer_ids": chunk})
        db.session.commit()

        logger.info("rows updated", extra={"offer_ids": chunk})


if __name__ == "__main__":
    import sys

    min_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    max_id_arg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    batch_size_arg = int(sys.argv[3]) if len(sys.argv) > 3 else None
    commit_size_arg = int(sys.argv[4]) if len(sys.argv) > 4 else None

    fix_offers_with_two_different_eans(min_id_arg, max_id_arg, batch_size_arg, commit_size_arg)
