"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-40610-move-past-collective-offer \
  -f NAMESPACE=move_past_collective_offer \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from unittest.mock import patch

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api.offer import move_collective_offer_for_regularization
from pcapi.core.finance import api as finance_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(collective_offer_id: int, destination_venue_id: int) -> None:
    collective_offer = db.session.get(educational_models.CollectiveOffer, collective_offer_id)
    destination_venue = db.session.get(offerers_models.Venue, destination_venue_id)

    assert collective_offer
    assert collective_offer.collectiveStock
    assert len(collective_offer.collectiveStock.collectiveBookings) == 1
    assert destination_venue
    assert destination_venue.managingOffererId == collective_offer.venue.managingOffererId

    with patch("pcapi.models.feature.FeatureToggle.VENUE_REGULARIZATION.is_active", return_value=True):
        with patch(
            "pcapi.core.educational.api.offer.check_can_move_collective_offer_venue", return_value=[destination_venue]
        ):
            move_collective_offer_for_regularization(collective_offer, destination_venue)

    collective_booking: educational_models.CollectiveBooking = collective_offer.collectiveStock.collectiveBookings[0]
    collective_booking.venueId = destination_venue_id
    db.session.add(collective_booking)
    finance_api.cancel_latest_event(collective_booking)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--collective-offer-id", type=int, required=True)
    parser.add_argument("--destination-venue-id", type=int, required=True)
    args = parser.parse_args()

    main(args.collective_offer_id, args.destination_venue_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
