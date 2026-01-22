"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39758-move-collective-offers \
  -f NAMESPACE=move_collective_offers \
  -f SCRIPT_ARGUMENTS="",

"""

import argparse
import json
import logging
import os

import sqlalchemy.orm as sa_orm

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def move_collective_offers(data: dict) -> None:
    old_venue = db.session.query(offerers_models.Venue).filter_by(id=data["old_venue_id"]).one()
    assert old_venue.managingOffererId == data["old_offerer_id"]

    new_venue = db.session.query(offerers_models.Venue).filter_by(id=data["new_venue_id"]).one()
    assert new_venue.managingOffererId == data["new_offerer_id"]

    collective_bookings = (
        db.session.query(educational_models.CollectiveBooking)
        .filter(
            educational_models.CollectiveBooking.id.in_(data["collective_booking_ids"]),
            educational_models.CollectiveBooking.offererId == data["old_offerer_id"],
            educational_models.CollectiveBooking.venueId == data["old_venue_id"],
        )
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveOffer
            )
        )
        .all()
    )

    logger.info("%d/%d collective bookings found", len(collective_bookings), len(data["collective_booking_ids"]))

    for collective_booking in collective_bookings:
        if collective_booking.status in {
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.PENDING,
        }:
            collective_offer = collective_booking.collectiveStock.collectiveOffer
            logger.info("Moving collective booking %d, offer %d", collective_booking.id, collective_offer.id)

            collective_booking.offererId = data["new_offerer_id"]
            collective_booking.venueId = data["new_venue_id"]
            collective_offer.venueId = data["new_venue_id"]

            if collective_offer.offererAddress:
                collective_offer.offererAddress = offerers_api.get_or_create_offer_location(
                    data["new_offerer_id"], collective_offer.offererAddress.addressId, label=old_venue.publicName
                )

            db.session.add(collective_booking)
            db.session.add(collective_offer)

    db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Move collective offers")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/moving_data.json", encoding="utf-8") as json_data:
        moving_data = json.load(json_data)
        for data in moving_data:
            move_collective_offers(data)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
