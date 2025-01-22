from typing import Collection

from pcapi.flask_app import app
from pcapi.repository import atomic
from pcapi.scripts.clean_offers_ean_title import utils
from pcapi.utils.chunks import get_chunks


# Mandatory since this module uses atomic() which needs an application context.
app.app_context().push()


QUERY = """
    SELECT
        id,
        substring("name" similar '%#"[[:digit:]]{13}#"%' escape '#') as ean,
        name,
        "subcategoryId",
        "isActive"
    FROM
        offer
    WHERE
        "name" similar to '%\\d{13}%'
        and "validation" != 'REJECTED'
        and "subcategoryId" not in (
            'SUPPORT_PHYSIQUE_FILM',
            'MATERIEL_ART_CREATIF',
            'ACHAT_INSTRUMENT',
            'LIVRE_PAPIER',
            'SUPPORT_PHYSIQUE_MUSIQUE_CD',
            'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE'
        )
    LIMIT
        10000
"""


def run() -> None:
    while True:
        rows = utils.get_offers_with_ean_inside_title(QUERY)
        if not rows:
            break

        parse_offers(rows)


def parse_offers(rows: Collection[utils.SharedOfferEanQueryRow]) -> None:
    for chunk in get_chunks(rows, chunk_size=2_000):
        reject_offers_with_eans_from_unauthorized_subcategories(chunk)


@atomic()
def reject_offers_with_eans_from_unauthorized_subcategories(
    offer_rows: Collection[utils.SharedOfferEanQueryRow],
) -> None:
    utils.reject_offers(offer_rows)


if __name__ == "__main__":
    app.app_context().push()
    run()
