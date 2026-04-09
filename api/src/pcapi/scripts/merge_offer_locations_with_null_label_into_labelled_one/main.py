"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bdalbianco/PC-40918 \
  -f NAMESPACE=merge_offer_locations_with_null_label_into_labelled_one \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import datetime
import logging
import os

import sqlalchemy.exc as sa_exc
from sqlalchemy import update

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)
FAILED_CHECKS: list = []
BATCH_SIZE = 5000
UPDATED_OFFERS_MAX_LIMIT = 2_000_000


def change_offers_location(
    offer_model: type[offers_models.Offer]
    | type[educational_models.CollectiveOffer]
    | type[educational_models.CollectiveOfferTemplate],
    old_location_id: int,
    new_location_id: int,
    apply: bool = False,
) -> bool:
    try:
        with atomic():
            batch_counter = 0
            subquery_for_batch = (
                db.session.query(offer_model.id)
                .filter(offer_model.offererAddressId == old_location_id)
                .limit(BATCH_SIZE)
                .subquery()
            )
            while db.session.query(subquery_for_batch).first() and batch_counter < UPDATED_OFFERS_MAX_LIMIT:
                try:
                    with atomic():
                        # raise sa_exc.OperationalError("hello", "parameter", "origin")
                        updated_offers = db.session.execute(
                            update(offer_model)
                            .where(offer_model.id.in_(subquery_for_batch))
                            .values(offererAddressId=new_location_id)
                        )
                        db.session.flush()
                        logger.info(
                            "updated %s offers for new location %s and %s in total",
                            updated_offers.rowcount,
                            new_location_id,
                            batch_counter,
                        )
                        batch_counter += updated_offers.rowcount
                except sa_exc.OperationalError:  # when updating multiple offers is too much
                    logger.info(
                        "batch update failed for new location %s - Trying to update offers one by one",
                        new_location_id,
                    )
                    try:
                        with atomic():
                            subquery = (
                                db.session.query(offer_model.id)
                                .filter(offer_model.offererAddressId == old_location_id)
                                .limit(1)
                                .subquery()
                            )
                            counter = 0
                            # raise sa_exc.OperationalError("hello", "parameter", "origin")
                            updated_offer = db.session.execute(
                                update(offer_model)
                                .where(offer_model.id.in_(subquery))
                                .values(offererAddressId=new_location_id)
                            )
                            while updated_offer.rowcount and counter < BATCH_SIZE:
                                db.session.flush()
                                if counter % 100 == 0:
                                    logger.info(
                                        "updated %s offers for new location %s one by one, currently %s done",
                                        counter,
                                        new_location_id,
                                        batch_counter,
                                    )
                                counter += 1
                                updated_offer = db.session.execute(
                                    update(offer_model)
                                    .where(offer_model.id.in_(subquery))
                                    .values(offererAddressId=new_location_id)
                                )
                            batch_counter += counter
                            if counter >= BATCH_SIZE:
                                logger.warning(
                                    "updated %s offers for new location %s, stopping now",
                                    BATCH_SIZE,
                                    new_location_id,
                                )
                    except sa_exc.OperationalError:
                        logger.info(
                            "Failed to update offers for new location %s, logging old location",
                            new_location_id,
                        )
                        FAILED_CHECKS.append({"old_location_id": old_location_id})
                        raise IndexError()
            if batch_counter >= UPDATED_OFFERS_MAX_LIMIT:
                logger.warning(
                    "updated %s offers for location %s, stopping now",
                    UPDATED_OFFERS_MAX_LIMIT,
                    new_location_id,
                )
                raise IndexError()
    except IndexError:
        return False
    return True


def main_func(
    apply: bool = False,
    locations_to_exclude: list[int] = [],
    max_execution_hours: int = 12,
) -> None:
    if locations_to_exclude:
        locations_doubles = (
            db.session.query(
                offerers_models.OffererAddress.venueId,
                offerers_models.OffererAddress.addressId,
                db.func.count(offerers_models.OffererAddress.id),
            )
            .join(offerers_models.OffererAddress.venue)
            .filter(
                offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
                (offerers_models.OffererAddress.label == None)
                | (offerers_models.OffererAddress.label == offerers_models.Venue.publicName),
                offerers_models.OffererAddress.id.notin_(locations_to_exclude),
            )
            .group_by(offerers_models.OffererAddress.venueId, offerers_models.OffererAddress.addressId)
            .having(db.func.count(offerers_models.OffererAddress.id) > 1)
            .all()
        )
    else:
        locations_doubles = (
            db.session.query(
                offerers_models.OffererAddress.venueId,
                offerers_models.OffererAddress.addressId,
                db.func.count(offerers_models.OffererAddress.id),
            )
            .join(offerers_models.OffererAddress.venue)
            .filter(
                offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
                (offerers_models.OffererAddress.label == None)
                | (offerers_models.OffererAddress.label == offerers_models.Venue.publicName),
            )
            .group_by(offerers_models.OffererAddress.venueId, offerers_models.OffererAddress.addressId)
            .having(db.func.count(offerers_models.OffererAddress.id) > 1)
            .all()
        )
    locations_doubles_to_check = list(
        locations_doubles
    )  # cast as python list so no sqlalchemy hijinks (remeber the list story half disappearing)
    logger.info(f"Found {len(locations_doubles_to_check)} locations to check for merging")
    i = 0
    start_time = datetime.datetime.now()
    for locations in locations_doubles_to_check:
        new_location_id = db.session.query(offerers_models.OffererAddress.id).filter(
            offerers_models.OffererAddress.venueId == locations.venueId,
            offerers_models.OffererAddress.addressId == locations.addressId,
            offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
            offerers_models.OffererAddress.label == None,
        )[0][0]
        old_location_id = db.session.query(offerers_models.OffererAddress.id).filter(
            offerers_models.OffererAddress.venueId == locations.venueId,
            offerers_models.OffererAddress.addressId == locations.addressId,
            offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
            offerers_models.OffererAddress.label == offerers_models.Venue.publicName,
        )[0][0]
        with atomic():
            if not apply:
                mark_transaction_as_invalid()
            if (
                change_offers_location(
                    offer_model=educational_models.CollectiveOfferTemplate,
                    old_location_id=old_location_id,
                    new_location_id=new_location_id,
                    apply=apply,
                )
                and change_offers_location(
                    offer_model=educational_models.CollectiveOffer,
                    old_location_id=old_location_id,
                    new_location_id=new_location_id,
                    apply=apply,
                )
                and change_offers_location(
                    offer_model=offers_models.Offer,
                    old_location_id=old_location_id,
                    new_location_id=new_location_id,
                    apply=apply,
                )
            ):
                db.session.query(offerers_models.OffererAddress).filter(
                    offerers_models.OffererAddress.id == old_location_id
                ).delete()
        i += 1
        if i % 1000 == 0:
            logger.info("Processed %d locations", i)
        if datetime.datetime.now() - start_time > datetime.timedelta(hours=max_execution_hours):
            logger.info(
                "Script has run for %d hours, %d locations remaining",
                max_execution_hours,
                len(locations_doubles_to_check) - i,
            )
            break


def handle_specific_locations(apply: bool = False, venueId: int = 0, addressId: int = 0) -> None:
    new_location_id = db.session.query(offerers_models.OffererAddress.id).filter(
        offerers_models.OffererAddress.venueId == venueId,
        offerers_models.OffererAddress.addressId == addressId,
        offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
        offerers_models.OffererAddress.label == None,
    )[0][0]
    old_location_id = db.session.query(offerers_models.OffererAddress.id).filter(
        offerers_models.OffererAddress.venueId == venueId,
        offerers_models.OffererAddress.addressId == addressId,
        offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
        offerers_models.OffererAddress.label == offerers_models.Venue.publicName,
    )[0][0]
    with atomic():
        if not apply:
            mark_transaction_as_invalid()
        if (
            change_offers_location(
                offer_model=educational_models.CollectiveOfferTemplate,
                old_location_id=old_location_id,
                new_location_id=new_location_id,
                apply=apply,
            )
            and change_offers_location(
                offer_model=educational_models.CollectiveOffer,
                old_location_id=old_location_id,
                new_location_id=new_location_id,
                apply=apply,
            )
            and change_offers_location(
                offer_model=offers_models.Offer,
                old_location_id=old_location_id,
                new_location_id=new_location_id,
                apply=apply,
            )
        ):
            db.session.query(offerers_models.OffererAddress).filter(
                offerers_models.OffererAddress.id == old_location_id
            ).delete()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--exclude-locations", nargs="*", type=int, default=[])
    parser.add_argument("--max-execution-hours", nargs=1, type=int, default=12)
    parser.add_argument("--venueid", nargs=1, type=int, default=1)
    parser.add_argument("--addressid", nargs=1, type=int, default=1)
    args = parser.parse_args()

    logger.info("Starting script")
    if args.venueid and args.addressid and args.venueid != 1 and args.addressid != 1:
        handle_specific_locations(apply=args.apply, venueId=args.venueid[0], addressId=args.addressid[0])
    else:
        main_func(
            apply=args.apply,
            locations_to_exclude=args.exclude_locations,
            max_execution_hours=args.max_execution_hours[0],
        )

    if FAILED_CHECKS:
        output_file = f"{os.environ['OUTPUT_DIRECTORY']}/merge_offer_locations.csv"
        logger.info("Exporting data to %s", output_file)
        with open(output_file, "w", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=["offer_id", "old_location_id"]
            )  # ici on met les entete de colonne
            writer.writeheader()
            for row in FAILED_CHECKS:
                writer.writerow(row)  # prend pour chaque valeur du dict et ecrit a la suite

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
