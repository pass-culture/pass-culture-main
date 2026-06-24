"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42558-move-collective-offer \
  -f NAMESPACE=move_collective_offer \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.api import get_or_create_offer_location
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(source_venue_id: int, destination_venue_id: int, collective_offer_id: int) -> None:
    source_venue = db.session.query(offerers_models.Venue).filter_by(id=source_venue_id).one()
    destination_venue = db.session.query(offerers_models.Venue).filter_by(id=destination_venue_id).one()

    assert source_venue.managingOffererId == destination_venue.managingOffererId

    collective_offer = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(
            educational_models.CollectiveOffer.venueId == source_venue_id,
            educational_models.CollectiveOffer.id == collective_offer_id,
        )
        .options(sa_orm.joinedload(educational_models.CollectiveOffer.offererAddress))
        .one()
    )

    logging.info("Move collective offer %d to venue %d", collective_offer.id, destination_venue_id)
    collective_offer.venueId = destination_venue_id
    if collective_offer.offererAddress:
        collective_offer.offererAddress = get_or_create_offer_location(
            offerer_id=destination_venue.managingOffererId,
            address_id=collective_offer.offererAddress.addressId,
            venue_id=destination_venue_id,
            label=collective_offer.offererAddress.label,
        )
    db.session.add(collective_offer)
    db.session.flush()

    collective_booking = (
        db.session.query(educational_models.CollectiveBooking)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .filter(
            educational_models.CollectiveBooking.venueId == source_venue_id,
            educational_models.CollectiveStock.collectiveOfferId == collective_offer_id,
        )
        .one()
    )

    logging.info("Move collective booking %d to venue %d", collective_booking.id, destination_venue_id)
    assert collective_booking.status == educational_models.CollectiveBookingStatus.USED
    collective_booking.venueId = destination_venue_id
    db.session.add(collective_booking)

    finance_event = (
        db.session.query(finance_models.FinanceEvent).filter_by(collectiveBookingId=collective_booking.id).one()
    )
    finance_event.venueId = destination_venue.id
    finance_event.pricingPointId = destination_venue.id
    db.session.add(finance_event)

    pricing = db.session.query(finance_models.Pricing).filter_by(collectiveBookingId=collective_booking.id).one()
    pricing.venueId = destination_venue.id
    pricing.pricingPointId = destination_venue.id
    db.session.add(pricing)

    db.session.flush()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--old-venue-id", type=int, required=True)
    parser.add_argument("--new-venue-id", type=int, required=True)
    parser.add_argument("--collective-offer-id", type=int, required=True)
    args = parser.parse_args()

    main(args.old_venue_id, args.new_venue_id, args.collective_offer_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
