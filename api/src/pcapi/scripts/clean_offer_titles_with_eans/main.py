from dataclasses import dataclass
from datetime import datetime
from datetime import timezone as tz
import functools
import logging
from typing import Collection

import sqlalchemy as sa

from pcapi.core.bookings import api as bookings_api
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offers.models import GcuCompatibilityType
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import atomic
from pcapi.repository import on_commit
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)

# Mandatory since this module uses atomic() which needs an application context.
app.app_context().push()


BOOKS_CDS_VINYLES_QUERY = """
    SELECT
        offer_sub_query.id,
        offer_sub_query.ean,
        offer_sub_query.name,
        offer_sub_query."subcategoryId",
        offer_sub_query."isActive",
        product.id is not null as exists,
        product.id as product_id,
        product.name as product_name,
        product."jsonData" as product_json_data,
        product."gcuCompatibilityType"
    FROM (
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
                'LIVRE_PAPIER',
                'SUPPORT_PHYSIQUE_MUSIQUE_CD',
                'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE'
            )
    ) offer_sub_query
    LEFT JOIN
        product on product."jsonData"->>'ean' = offer_sub_query.ean
    LIMIT
        1000
"""


@dataclass(frozen=True)
class OfferEanQueryRow:
    id: int
    ean: str
    name: str
    subcategory: str
    is_active: bool
    exists: bool
    product_id: int | None
    product_name: str | None
    product_json_data: dict | None
    gcu_compatibility: str | None


def get_offers_with_ean_inside_title() -> Collection[OfferEanQueryRow]:
    query = sa.text(BOOKS_CDS_VINYLES_QUERY)
    rows = []
    for row in db.session.execute(query):
        rows.append(
            OfferEanQueryRow(
                id=row[0],
                ean=row[1],
                name=row[2],
                subcategory=row[3],
                is_active=row[4],
                exists=row[5],
                product_id=row[6],
                product_name=row[7],
                product_json_data=row[8],
                gcu_compatibility=row[9],
            )
        )

    return rows


def run() -> None:
    while True:
        rows = get_offers_with_ean_inside_title()
        if not rows:
            break

        parse_offers(rows)


def parse_offers(rows: Collection[OfferEanQueryRow]) -> None:
    for chunk in get_chunks(rows, chunk_size=100):

        unknown_offer_rows = []
        gcu_incompatible_offer_rows = []
        legit_offer_rows = []

        for offer_row in chunk:
            if not offer_row.exists:
                unknown_offer_rows.append(offer_row)
            elif offer_row.gcu_compatibility != GcuCompatibilityType.COMPATIBLE.value:
                gcu_incompatible_offer_rows.append(offer_row)
            else:
                legit_offer_rows.append(offer_row)

        reject_offers(unknown_offer_rows)
        reject_offers(gcu_incompatible_offer_rows)
        update_legit_offers(legit_offer_rows)


@atomic()
def update_legit_offers(offer_rows: Collection[OfferEanQueryRow]) -> None:
    ids = {row.id for row in offer_rows}
    legit_offers = Offer.query.filter(Offer.id.in_(ids))

    offer_to_product = {row.id: row for row in offer_rows}

    for offer in legit_offers:
        offer.name = offer_to_product[offer.id].product_name

        if offer_to_product[offer.id].product_json_data:
            offer.extraData = offer_to_product[offer.id].product_json_data


@atomic()
def reject_offers(offer_rows: Collection[OfferEanQueryRow]) -> None:
    def cancel_booking(offer: Offer) -> None:
        cancelled_bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)
        for booking in cancelled_bookings:
            transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email(
                booking, rejected_by_fraud_action=True
            )

    def notify_offerer(offer: Offer) -> None:
        if offer.venue.bookingEmail:
            recipients = [offer.venue.bookingEmail]
        else:
            recipients = [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]

        offer_data = transactional_mails.get_email_data_from_offer(
            offer, offer.validation, OfferValidationStatus.REJECTED
        )
        on_commit(
            functools.partial(
                transactional_mails.send_offer_validation_status_update_email,
                offer_data,
                recipients,
            )
        )

    ids = {row.id for row in offer_rows}
    base_query = Offer.query.filter(
        Offer.id.in_(ids),
        Offer.status != OfferValidationStatus.REJECTED.value,
    )

    for offer in base_query:
        cancel_booking(offer)
        notify_offerer(offer)

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


if __name__ == "__main__":
    app.app_context().push()
    run()
