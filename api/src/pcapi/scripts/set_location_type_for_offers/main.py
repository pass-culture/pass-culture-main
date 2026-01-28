"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bdalbianco/PC-37992_set_location_type_for_offers_locations \
  -f NAMESPACE=set_location_type_for_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.models import LocationType
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

BATCH_SIZE = 50


# garder version actuelle, tester et si marche pas on passe en table par table


@atomic()
def find_venue_id(location: offerers_models.OffererAddress, not_dry: bool) -> None:
    if not not_dry:
        mark_transaction_as_invalid()
    venue_id = (
        db.session.query(educational_models.CollectiveOfferTemplate.venueId)
        .where(
            educational_models.CollectiveOfferTemplate.locationType
            == educational_models.CollectiveLocationType.ADDRESS,
            educational_models.CollectiveOfferTemplate.offererAddressId == location.id,
        )
        .first()
    )
    if not venue_id:
        venue_id = (
            db.session.query(educational_models.CollectiveOffer.venueId)
            .where(
                educational_models.CollectiveOffer.locationType == educational_models.CollectiveLocationType.ADDRESS,
                educational_models.CollectiveOffer.offererAddressId == location.id,
            )
            .first()
        )
        if not venue_id:
            venue_id = (
                db.session.query(offers_models.Offer.venueId)
                .where(offers_models.Offer.offererAddressId == location.id)
                .first()
            )
            if not venue_id:
                logger.warning(f"No offer found for location id {location.id}, skipping...")
                return
    try:
        with atomic():
            location.type = LocationType.OFFER_LOCATION
            location.venueId = venue_id[0]
            db.session.flush()
    except sa.exc.IntegrityError as e:
        logger.error(f"Error flushing location id {location.id}: {e}")
        unique_location = (
            db.session.query(offerers_models.OffererAddress)
            .filter(offerers_models.OffererAddress.addressId == location.addressId)
            .filter(offerers_models.OffererAddress.offererId == location.offererId)
            .filter(offerers_models.OffererAddress.label == location.label)
            .filter(offerers_models.OffererAddress.venueId == venue_id[0])
            .filter(offerers_models.OffererAddress.type == LocationType.OFFER_LOCATION)
        ).one()
        db.session.query(offers_models.Offer).filter(offers_models.Offer.offererAddressId == location.id).update(
            {offers_models.Offer.offererAddressId: unique_location.id}
        )
        db.session.query(educational_models.CollectiveOfferTemplate).filter(
            educational_models.CollectiveOfferTemplate.offererAddressId == location.id
        ).update({educational_models.CollectiveOfferTemplate.offererAddressId: unique_location.id})
        db.session.query(educational_models.CollectiveOffer).filter(
            educational_models.CollectiveOffer.offererAddressId == location.id
        ).update({educational_models.CollectiveOffer.offererAddressId: unique_location.id})
        db.session.flush()


@atomic()
def find_all_venues(locations: list[offerers_models.OffererAddress], not_dry: bool) -> None:
    remaining_location_ids_to_process = [location.id for location in locations]
    locations_found_in_template_offers = (
        db.session.query(
            educational_models.CollectiveOfferTemplate.offererAddressId,
            educational_models.CollectiveOfferTemplate.venueId,
        )
        .where(
            educational_models.CollectiveOfferTemplate.locationType == educational_models.CollectiveLocationType.ADDRESS
        )
        .where(educational_models.CollectiveOfferTemplate.offererAddressId.in_(remaining_location_ids_to_process))
        .all()
    )
    logger.info("%d locations found in template offers", len(locations_found_in_template_offers))
    locations_ids_from_template_offers = [location_id[0] for location_id in locations_found_in_template_offers]
    remaining_location_ids_to_process = [
        location for location in remaining_location_ids_to_process if location not in locations_ids_from_template_offers
    ]
    locations_found_in_collective_offers = (
        db.session.query(
            educational_models.CollectiveOffer.offererAddressId, educational_models.CollectiveOffer.venueId
        )
        .where(educational_models.CollectiveOffer.locationType == educational_models.CollectiveLocationType.ADDRESS)
        .where(educational_models.CollectiveOffer.offererAddressId.in_(remaining_location_ids_to_process))
        .all()
    )
    logger.info("%d locations found in collective offers", len(locations_found_in_collective_offers))
    collective_offers_ids = [location_id[0] for location_id in locations_found_in_collective_offers]
    remaining_location_ids_to_process = [
        location for location in remaining_location_ids_to_process if location not in collective_offers_ids
    ]
    location_found_in_individual_offers = (
        db.session.query(offers_models.Offer.offererAddressId, offers_models.Offer.venueId)
        .where(offers_models.Offer.offererAddressId.in_(remaining_location_ids_to_process))
        .all()
    )
    logger.info("%d locations found in individual offers", len(location_found_in_individual_offers))
    all_venue_ids = (
        locations_found_in_template_offers + locations_found_in_collective_offers + location_found_in_individual_offers
    )
    for location in locations:
        location.type = LocationType.OFFER_LOCATION
        location.venueId = next((offer[1] for offer in all_venue_ids if offer[0] == location.id), None)
    if not not_dry:
        mark_transaction_as_invalid()
    else:
        db.session.flush()


def bettermain(not_dry: bool) -> None:
    """60 batchs de 1000 * 90 000  + 1000 * 700 000 + 1000 * 1M"""
    target = (
        db.session.query(sa.func.count(offerers_models.OffererAddress.id))
        .filter(offerers_models.OffererAddress.type.is_(None))
        .scalar()
    )
    logger.info(f"Total locations to process: {target}")
    i = 0
    while i < target:
        locations_to_set = (
            db.session.query(offerers_models.OffererAddress)
            .filter(offerers_models.OffererAddress.type.is_(None))
            .limit(BATCH_SIZE)
            .offset(i)
            .all()
        )
        find_all_venues(locations_to_set, not_dry)
        logger.info("Done for batch %d to %d", i, i + BATCH_SIZE)
        i += BATCH_SIZE


def main(not_dry: bool) -> None:
    """for 60 000 locations :90 000 * 700 000 * 1M?"""
    locations_to_set = db.session.query(offerers_models.OffererAddress).filter(
        offerers_models.OffererAddress.type.is_(None)
    )
    for location in locations_to_set:
        find_venue_id(location, not_dry)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
