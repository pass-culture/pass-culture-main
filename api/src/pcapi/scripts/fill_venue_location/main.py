"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39904-remettre-des-localisations-sur-les-venues-en-integration \
  -f NAMESPACE=fill_venue_location \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    for venue in db.session.query(offerers_models.Venue).all():
        print("venue: %s (%s)" % (venue.id, venue.managingOffererId))
        if venue.offererAddress:
            # Skip if the venue already has a location
            print("Skipping, already has a location")
            continue

        # If there's only one location, let's just use it
        if (
            db.session.query(offerers_models.OffererAddress)
            .filter(offerers_models.OffererAddress.offererId == venue.managingOffererId)
            .count()
            == 1
        ):
            print("Offerer has only one location")
            location = (
                db.session.query(offerers_models.OffererAddress)
                .filter(offerers_models.OffererAddress.offererId == venue.managingOffererId)
                .first()
            )
            assert location
            offerer_address = offerers_models.OffererAddress(
                offererId=venue.managingOffererId,
                addressId=location.addressId,
                type=offerers_models.LocationType.VENUE_LOCATION,
                label=None,
                venueId=venue.id,
            )
        else:
            location = (
                db.session.query(offerers_models.OffererAddress)
                .join(offers_models.Offer, offers_models.Offer.offererAddressId == offerers_models.OffererAddress.id)
                .filter(offers_models.Offer.venueId == venue.id)
                .order_by(offers_models.Offer.id)
                .first()
            )
            if location:
                print("First offer has a location")
                offerer_address = offerers_models.OffererAddress(
                    offererId=venue.managingOffererId,
                    addressId=location.addressId,
                    type=offerers_models.LocationType.VENUE_LOCATION,
                    label=None,
                    venueId=venue.id,
                )
            else:
                # Default to a fixed address
                print("Using default")
                offerer_address = offerers_models.OffererAddress(
                    offererId=venue.managingOffererId,
                    addressId=1509,
                    type=offerers_models.LocationType.VENUE_LOCATION,
                    label=None,
                    venueId=venue.id,
                )
        db.session.add(offerer_address)
        db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
