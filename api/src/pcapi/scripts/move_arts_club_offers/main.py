"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=prd \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=pc-41846-move-arts-club-offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from functools import partial

from pcapi.app import app
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.offers import models as offers_models
from pcapi.core.search import IndexationReason
from pcapi.models import db
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)

SOURCE_VENUE_ID = 52164
DESTINATION_VENUE_ID = 157844
OFFER_IDS = [
    408522829,
    408523512,
    408522602,
    409635260,
    409635307,
    408685784,
    405847303,
    405846998,
    412125905,
    412025544,
    412015351,
    411850197,
]


def main() -> None:
    assert (
        db.session.query(offers_models.PriceCategory).filter(offers_models.PriceCategory.offerId.in_(OFFER_IDS)).count()
        == 0
    )
    assert db.session.query(educational_models.CollectiveOffer).filter_by(venueId=SOURCE_VENUE_ID).count() == 0

    offers = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.venueId == SOURCE_VENUE_ID, offers_models.Offer.id.in_(OFFER_IDS))
        .all()
    )
    logger.info("%d offers found", len(offers))

    for offer in offers:
        logging.info("Move offer %d to venue %d", offer.id, DESTINATION_VENUE_ID)
        offer.venueId = DESTINATION_VENUE_ID
        assert offer.offererAddressId is None, offer.id
        db.session.add(offer)
        on_commit(partial(search.async_index_offer_ids, [offer.id], reason=IndexationReason.OFFER_UPDATE))

    bookings = (
        db.session.query(bookings_models.Booking)
        .join(bookings_models.Booking.stock)
        .filter(
            bookings_models.Booking.venueId == SOURCE_VENUE_ID,
            offers_models.Stock.offerId.in_(OFFER_IDS),
        )
        .all()
    )
    logger.info("%d bookings found", len(bookings))

    for booking in bookings:
        logging.info("Move booking %s to venue %d", booking.token, DESTINATION_VENUE_ID)
        booking.venueId = DESTINATION_VENUE_ID
        db.session.add(booking)

    db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
