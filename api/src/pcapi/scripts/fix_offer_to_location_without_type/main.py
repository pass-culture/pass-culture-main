"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39634-amelioration-des-localisations-repasser-les-offres-de-l-api-publique-sur-des-oa-sans-type \
  -f NAMESPACE=fix_offer_to_location_without_type \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


BATCH_SIZE = 1000


def main(not_dry: bool) -> None:
    nb_OA = (
        db.session.query(sa.func.count(offerers_models.OffererAddress.id))
        .filter(offerers_models.OffererAddress.type == offerers_models.LocationType.VENUE_LOCATION)
        .scalar()
    )
    # using limit at 1000 and offset keeps the query planer with faster requests than using
    # cursors or whatever
    i = 0
    while i < nb_OA:
        location_ids = (
            db.session.query(offerers_models.OffererAddress.id)
            .filter(offerers_models.OffererAddress.type == offerers_models.LocationType.VENUE_LOCATION)
            .order_by(offerers_models.OffererAddress.id)
            .limit(BATCH_SIZE)
            .offset(i)
        )
        locations_offers_mapping: dict[int, list[int]] = {}
        locations_venues_mapping: dict[int, int] = {}
        offer_per_location_query = (
            db.session.query(offers_models.Offer.id, offers_models.Offer.offererAddressId, offers_models.Offer.venueId)
            .filter(offers_models.Offer.offererAddressId.in_(location_ids))
            .all()
        )
        for row in offer_per_location_query:
            locations_offers_mapping.setdefault(row[1], []).append(row[0])
            locations_venues_mapping[row[1]] = row[2]

        logger.info(
            "Batch %i (size=%i) found: %s", i, BATCH_SIZE, {k: len(v) for k, v in locations_offers_mapping.items()}
        )

        for offerer_address_id, offer_ids in locations_offers_mapping.items():
            venue = (
                db.session.query(offerers_models.Venue)
                .filter(offerers_models.Venue.id == locations_venues_mapping[offerer_address_id])
                .one()
            )
            venue_location = (
                db.session.query(offerers_models.OffererAddress)
                .filter(offerers_models.OffererAddress.id == offerer_address_id)
                .one()
            )
            # identify the "real" location
            offer_location = offerers_api.get_or_create_offer_location(
                venue.managingOffererId, venue_location.addressId, venue.publicName
            )
            # move the associated offers to the new location
            db.session.query(offers_models.Offer).filter(
                offers_models.Offer.id.in_(offer_ids),
            ).update({"offererAddressId": offer_location.id})

        i += BATCH_SIZE


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
