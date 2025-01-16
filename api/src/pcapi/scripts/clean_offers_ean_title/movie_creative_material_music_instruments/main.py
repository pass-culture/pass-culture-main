from typing import Collection

from pcapi.core.offers.models import Offer
from pcapi.flask_app import app
from pcapi.models import db
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
        and "subcategoryId" in (
            'SUPPORT_PHYSIQUE_FILM',
            'MATERIEL_ART_CREATIF',
            'ACHAT_INSTRUMENT'
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

        ean_as_name_rows = set()
        other_rows = set()

        for offer_row in chunk:
            if offer_row.name.strip().lower() == offer_row.ean:
                ean_as_name_rows.add(offer_row)
            else:
                other_rows.add(offer_row)

        reject_offers_with_ean_as_name(ean_as_name_rows)
        update_legit_offers(other_rows)


@atomic()
@utils.retry_and_log
def reject_offers_with_ean_as_name(offer_rows: Collection[utils.SharedOfferEanQueryRow]) -> None:
    utils.reject_offers(offer_rows)


@atomic()
@utils.retry_and_log
def update_legit_offers(offer_rows: Collection[utils.SharedOfferEanQueryRow]) -> None:
    ids = {row.id for row in offer_rows}
    offer_eans = {row.id: row.ean for row in offer_rows}

    legit_offers = Offer.query.filter(Offer.id.in_(ids))

    with atomic():
        for offer in legit_offers:
            offer.name = offer.name.replace(offer_eans[offer.id], "").replace("  ", "")
            offer.extraData = {**offer.extraData, "ean": offer_eans[offer.id]}
            db.session.add(offer)
