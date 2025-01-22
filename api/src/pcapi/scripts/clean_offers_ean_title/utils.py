from dataclasses import dataclass
from datetime import datetime
from datetime import timezone as tz
import functools
import logging
from typing import Callable
from typing import Collection

import sqlalchemy as sa

from pcapi.core.bookings import api as bookings_api
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import atomic
from pcapi.repository import on_commit
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SharedOfferEanQueryRow:
    id: int
    ean: str
    name: str
    subcategory: str
    is_active: bool


def get_offers_with_ean_inside_title(raw_query: str) -> Collection[SharedOfferEanQueryRow]:
    query = sa.text(raw_query)

    rows = []
    for row in db.session.execute(query):
        rows.append(
            SharedOfferEanQueryRow(
                id=row[0],
                ean=row[1],
                name=row[2],
                subcategory=row[3],
                is_active=row[4],
            )
        )

    return rows


def reject_offers(offer_rows: Collection) -> None:
    def cancel_booking(offer: Offer) -> None:
        cancelled_bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)
        for booking in cancelled_bookings:
            on_commit(
                functools.partial(
                    transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email,
                    booking,
                    rejected_by_fraud_action=True,
                )
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
