from dataclasses import dataclass
from datetime import datetime
from datetime import timezone as tz
import logging
from typing import Collection
from typing import Generator

import sqlalchemy as sa

from pcapi.core.bookings import api as bookings_api
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import atomic
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)

# Mandatory since this module uses atomic() which needs an application context.
app.app_context().push()


MOVIES_ART_STUFF_MUSIC_INSTRUMENTS_WITH_EAN_INSIDE_TITLE_QUERY = """
    SELECT
        offer.id as offer_id,
        btrim(offer.name) as offer_name,
        substring("name" similar '%#"[[:digit:]]{13}#"%' escape '#') as ean
    FROM
        offer
    WHERE
        -- offer with ean inside title
        offer."name" similar to '%\\d{13}%'
        -- not all subcategories can have EAN
        AND offer."subcategoryId" in (
             'SUPPORT_PHYSIQUE_FILM',
             'MATERIEL_ART_CREATIF',
             'ACHAT_INSTRUMENT'
        )
        AND offer.validation != 'REJECTED'
        AND offer."isActive" is true
        AND offer.id >= :lower_bound
        AND offer.id < :upper_bound
"""


@dataclass(frozen=True)
class OfferRow:
    offer_id: int
    offer_name: str
    ean: str


def handle_offers_with_ean_inside_title(
    min_id: int | None = None, max_id: int | None = None, batch_size: int | None = None, commit_size: int | None = None
) -> None:
    if not commit_size:
        commit_size = 250

    rows_iterator = get_offers_with_ean_inside_title(min_id=min_id, max_id=max_id, batch_size=batch_size)
    for idx, chunk in enumerate(get_chunks(rows_iterator, commit_size)):
        logger.info("start loop #%d with %d ids...", idx, len(chunk))

        offers_to_reject = [row for row in chunk if len(row.offer_name) == len(row.ean)]
        offers_to_update = [row for row in chunk if len(row.offer_name) > len(row.ean)]

        assert len(offers_to_reject) + len(offers_to_update) == len(chunk)

        reject_offers(offers_to_reject)
        update_offers_names(offers_to_update)


def get_offers_with_ean_inside_title(
    min_id: int | None = None, max_id: int | None = None, batch_size: int | None = None
) -> Generator[OfferRow, None, None]:
    query = sa.text(MOVIES_ART_STUFF_MUSIC_INSTRUMENTS_WITH_EAN_INSIDE_TITLE_QUERY)

    if not min_id:
        min_id = list(db.session.execute("SELECT min(id) FROM offer"))[0][0]

    if not max_id:
        max_id = list(db.session.execute("SELECT max(id) FROM offer"))[0][0]

    assert min_id is not None
    assert max_id is not None

    # the else clause is mostly needed for local and testing
    # environments where the number of offer will be low.
    if not batch_size:
        batch_size = 10_000 if max_id > 100_000 else max((min_id - max_id) // 10, 2)

    for upper_bound in reversed(range(min_id, max_id + batch_size + 1, batch_size)):
        query_params = {"upper_bound": upper_bound, "lower_bound": upper_bound - batch_size}
        logger.info("yield rows from %d to %d", upper_bound - batch_size, upper_bound)
        for row in db.session.execute(query, query_params):
            yield OfferRow(offer_id=row[0], offer_name=row[1], ean=row[2])


@atomic()
def reject_offers(offer_rows: Collection[OfferRow]) -> None:
    offer_ids = [row.offer_id for row in offer_rows]
    base_query = Offer.query.filter(
        Offer.id.in_(offer_ids),
        Offer.status != OfferValidationStatus.REJECTED.value,
    )

    for offer in base_query:
        cancelled_bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)
        for booking in cancelled_bookings:
            transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email(
                booking, rejected_by_fraud_action=True
            )

    base_query.update(
        {
            "validation": OfferValidationStatus.REJECTED.value,
            "lastValidationDate": datetime.now(tz.utc),  # pylint: disable=datetime-now
            "lastValidationType": OfferValidationType.AUTO.value,
            "lastValidationAuthorUserId": None,
            "isActive": False,
        },
        synchronize_session=False,
    )

    logger.info("%d offers rejected", len(offer_ids))


@atomic()
def update_offers_names(offer_rows: Collection[OfferRow]) -> None:
    offer_ean_mapping = {row.offer_id: row.ean for row in offer_rows}
    base_query = Offer.query.filter(
        Offer.id.in_(offer_ean_mapping.keys()),
        Offer.status != OfferValidationStatus.REJECTED.value,
    )

    for offer in base_query:
        offer.name = (
            offer.name.replace(f"#{offer_ean_mapping[offer.id]}", "")
            .replace(f"# {offer_ean_mapping[offer.id]}", "")
            .replace(f"-{offer_ean_mapping[offer.id]}", "")
            .replace(f"- {offer_ean_mapping[offer.id]}", "")
            .replace(f"{offer_ean_mapping[offer.id]}", "")
            .replace("  ", " ")
            .strip()
        )
        offer.ean = offer_ean_mapping[offer.id]

    logger.info("%d offers updated", len(offer_rows))


if __name__ == "__main__":
    import sys

    app.app_context().push()

    min_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    max_id_arg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    batch_size_arg = int(sys.argv[3]) if len(sys.argv) > 3 else None
    commit_size_arg = int(sys.argv[4]) if len(sys.argv) > 4 else None

    handle_offers_with_ean_inside_title(min_id_arg, max_id_arg, batch_size_arg, commit_size_arg)
