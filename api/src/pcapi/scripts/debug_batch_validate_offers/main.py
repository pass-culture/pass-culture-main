"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/debug_batch_validate_offers_data/api/src/pcapi/scripts/debug_batch_validate_offers/main.py

"""

import argparse
import datetime
import json
import logging
import os
import time

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType


logger = logging.getLogger(__name__)


def debug_batch_validate_offers_data(offer_ids: list[int]) -> None:
    max_price_subquery = (
        sa.select(sa.func.max(offers_models.Stock.price))
        .select_from(offers_models.Stock)
        .filter(
            offers_models.Stock.offerId == offers_models.Offer.id,
            sa.not_(offers_models.Stock.isSoftDeleted),
        )
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )
    offers = (
        db.session.query(
            offers_models.Offer,
            max_price_subquery.label("max_price"),
        )
        .filter(offers_models.Offer.id.in_(offer_ids))
        .options(
            sa_orm.joinedload(offers_models.Offer.venue).load_only(
                offerers_models.Venue.bookingEmail, offerers_models.Venue.name, offerers_models.Venue.publicName
            ),
            sa_orm.joinedload(offers_models.Offer.offererAddress).options(
                sa_orm.joinedload(offerers_models.OffererAddress.address),
                sa_orm.selectinload(offerers_models.OffererAddress.venues),
            ),
        )
    ).all()

    output_dir = os.environ.get("OUTPUT_DIRECTORY") or os.path.abspath(os.path.dirname(__file__))
    assert output_dir is not None  # helps mypy
    output_file = os.path.join(output_dir, f"debug_batch_validate_offers_data_{int(time.time())}.txt")

    with open(output_file, "w", newline="") as f:
        f.write("offers: %s\n" % offers)

        for offer, max_price in offers:
            _ = offer.validation
            offer.validation = offers_models.OfferValidationStatus.APPROVED
            offer.lastValidationDate = datetime.datetime.utcnow()
            offer.lastValidationType = OfferValidationType.MANUAL
            offer.lastValidationAuthorUserId = None

            is_not_a_future_offer = (
                offer.publicationDatetime is None
                or offer.publicationDatetime <= datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            )
            if is_not_a_future_offer:
                offer.publicationDatetime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            if offer.isThing:
                offer.lastValidationPrice = max_price

            db.session.add(offer)

            recipients = (
                [offer.venue.bookingEmail]
                if offer.venue.bookingEmail
                else [
                    recipient.user.email
                    for recipient in offer.venue.managingOfferer.UserOfferers
                    if recipient.isValidated
                ]
            )

            offer_data = transactional_mails.get_email_data_from_offer(
                offer, offers_models.OfferValidationStatus.PENDING, offers_models.OfferValidationStatus.APPROVED
            )

            f.write("-----\n")
            f.write("offer: %s %s\n" % (offer, offer.name))
            f.write("max_price: %s\n" % max_price)
            f.write("offer.venue: %s\n" % offer.venue)
            f.write("offer.venue.bookingEmail: %s\n" % offer.venue.bookingEmail)
            f.write("recipients: %s\n" % recipients)
            f.write("offer_data: %s\n" % offer_data)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--offer-ids", help="JSON list of offer IDs", required=True)
    args = parser.parse_args()

    offer_ids = json.loads(args.offer_ids)
    debug_batch_validate_offers_data(offer_ids)

    db.session.rollback()
