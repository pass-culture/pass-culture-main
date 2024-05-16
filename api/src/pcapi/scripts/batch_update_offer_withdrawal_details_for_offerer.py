"""
Fetch offers from database and update their withdrawal details on Batch.
"""

import math

import sqlalchemy as sa
from sqlalchemy import func

from pcapi.core.offers.models import Offer
from pcapi.models import db


def batch_update_offer_withdrawal_details_for_offerer(
    offerer_id: int, withdrawal_details: str, batch_size: int = 1000
) -> None:
    min_id = db.session.query(func.min(Offer.id)).scalar()
    max_id = db.session.query(func.max(Offer.id)).scalar()
    number_of_batch = math.ceil(max_id / batch_size)
    number_of_batch_done = 0
    ranges = [(i, i + batch_size) for i in range(min_id, max_id + 1, batch_size)]
    for start, end in ranges:
        db.session.execute(
            sa.text(
                """
            UPDATE offer
            SET "withdrawalDetails" = :withdrawal_details
            FROM venue
            WHERE
              offer."venueId" = venue.id
              AND offer.id BETWEEN :start AND :end
              AND offer."isActive" IS TRUE
              AND offer."withdrawalDetails" IS NULL
              AND venue."managingOffererId" = :offerer_id
            """
            ),
            {"start": start, "end": end, "withdrawal_details": withdrawal_details, "offerer_id": offerer_id},
        )
        db.session.commit()
        number_of_batch_done += 1
        print("Withdrawal details update ongoing... batch %s of %s" % (number_of_batch_done, number_of_batch))
