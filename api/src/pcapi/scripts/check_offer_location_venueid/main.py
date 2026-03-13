"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bdalbianco/PC-40096 \
  -f NAMESPACE=check_offer_location_venueid \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os

import sqlalchemy.exc as sa_exc
from sqlalchemy import update

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)
FAILED_CHECKS = []


@atomic()
def fix_incorrect_offers(
    location: offerers_models.OffererAddress,
    is_dry: bool,
    incorrect_offers_venueIds: list,
    offer_model: type[offers_models.Offer]
    | type[educational_models.CollectiveOffer]
    | type[educational_models.CollectiveOfferTemplate],
) -> None:
    if is_dry:
        mark_transaction_as_invalid()
    for venueid in incorrect_offers_venueIds:
        appropriate_location = offerers_api.get_or_create_offer_location(
            offerer_id=location.offererId,
            address_id=location.addressId,
            label=location.label,
            venue_id=venueid[0],
        )
        try:
            all_offers = db.session.query(offer_model).filter(
                offer_model.offererAddressId == location.id, offer_model.venueId == venueid[0]
            )
            all_offers.update({offer_model.offererAddressId: appropriate_location.id}, synchronize_session=False)
        except sa_exc.OperationalError as exc:  # when updating multiple offers is too much
            logger.info("Exception %s - Trying to update offer one by one", str(exc))
            for offer_id in all_offers.all():
                with atomic():
                    db.session.execute(
                        update(offer_model)
                        .where(offer_model.id == offer_id)
                        .values(offererAddressId=appropriate_location.id)
                    )


def find_incorrect_offers(
    location: offerers_models.OffererAddress,
    is_dry: bool,
    offer_model: type[offers_models.Offer]
    | type[educational_models.CollectiveOffer]
    | type[educational_models.CollectiveOfferTemplate],
) -> None:
    try:
        with atomic():
            incorrect_offers_venueIds = (
                db.session.query(offer_model.venueId)
                .distinct()
                .where(
                    offer_model.offererAddressId == location.id,
                    offer_model.venueId != location.venueId,
                )
                .all()
            )
    except sa_exc.OperationalError as exc:  # when there are too many offers to check
        logger.info("offererAddressId %s has too many offers, doing it one by one %s", location.id, exc)
        try:
            with atomic():
                while one_incorrect_offers_venueId := (
                    db.session.query(offer_model.venueId)
                    .where(
                        offer_model.offererAddressId == location.id,
                        offer_model.venueId != location.venueId,
                    )
                    .first()
                ):
                    incorrect_offers_venueIds = [one_incorrect_offers_venueId]
                    fix_incorrect_offers(
                        location,
                        is_dry=is_dry,
                        incorrect_offers_venueIds=incorrect_offers_venueIds,
                        offer_model=offer_model,
                    )
        except sa_exc.OperationalError as exc:
            FAILED_CHECKS.append({"location_id": location.id, "unrelated_to_the_venueID": location.venueId})
    else:
        if incorrect_offers_venueIds:
            fix_incorrect_offers(
                location, is_dry=is_dry, incorrect_offers_venueIds=incorrect_offers_venueIds, offer_model=offer_model
            )


def main(is_dry: bool) -> None:
    offer_locations_to_check = (
        db.session.query(offerers_models.OffererAddress)
        .filter(offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION)
        .all()
    )
    _ = 0
    for location in offer_locations_to_check:
        try:
            with atomic():
                db.session.query(offerers_models.Venue.id).filter(
                    offerers_models.Venue.managingOffererId == location.offererId
                ).one()
        except sa_exc.MultipleResultsFound:
            find_incorrect_offers(location, is_dry=is_dry, offer_model=educational_models.CollectiveOfferTemplate)
            find_incorrect_offers(location, is_dry=is_dry, offer_model=educational_models.CollectiveOffer)
            find_incorrect_offers(location, is_dry=is_dry, offer_model=offers_models.Offer)
            _ += 1
        if _ % 100 == 0:
            logger.info("Checked %s offer locations with error risk", _)
    if FAILED_CHECKS:
        output_file = f"{os.environ['OUTPUT_DIRECTORY']}/check_offer_location_venueId_big_OAs.csv"
        logger.info("Exporting data to %s", output_file)
        with open(output_file, "w", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=["location_id", "unrelated_to_the_venueID"]
            )  # ici on met les entete de colonne
            writer.writeheader()
            for row in FAILED_CHECKS:
                writer.writerow(row)  # prend pour chaque valeur du dict et ecrit a la suite


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    logger.info("Starting script")
    main(is_dry=not args.not_dry)
    logger.info("Script finished")
