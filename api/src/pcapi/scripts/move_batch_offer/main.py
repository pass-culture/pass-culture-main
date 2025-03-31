"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-35283-move-offer-batch-check-venue/api/src/pcapi/scripts/move_batch_offer/main.py

"""

import csv
import logging
import os
import typing

from sqlalchemy import exc as sqla_exc

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository


logger = logging.getLogger(__name__)

ORGINE_VENUE_ID_HEADER = "origine_venue_id"
DESTINATION_VENUE_ID_HEADER = "destination_venue_id"


def get_venues_to_move_from_csv_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/venues_to_move.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def extract_invalid_venues_to_csv(invalid_venues: list[tuple[int, int, str]]) -> None:
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/venues_impossible_to_move.csv"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([ORGINE_VENUE_ID_HEADER, DESTINATION_VENUE_ID_HEADER, "Reason"])
        writer.writerows(invalid_venues)


def check_destination_venue_compatibility(
    origine_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> tuple[int, int, str] | None:
    venues_choices = offerers_repository.get_offerers_venues_with_pricing_point(
        origine_venue,
        include_without_pricing_points=True,
        only_similar_pricing_points=True,
        filter_same_bank_account=True,
    )
    if not venues_choices:
        logger.info(
            "No compatible venue was found for venue %d. Destination venue was %d",
            origine_venue.id,
            destination_venue.id,
        )
        return origine_venue.id, destination_venue.id, "No compatible venue"
    if destination_venue not in venues_choices:
        logger.info("Destination venue %d is not valid for venue %d", destination_venue.id, origine_venue.id)
        return origine_venue.id, destination_venue.id, "Destination venue not valid"
    return None


def main() -> None:
    invalid_venues = []
    for row in get_venues_to_move_from_csv_file():
        origine_venue_id = int(row[ORGINE_VENUE_ID_HEADER])
        destination_venue_id = int(row[DESTINATION_VENUE_ID_HEADER])
        try:
            origine_venue = offerers_models.Venue.query.filter(offerers_models.Venue.id == origine_venue_id).one()
            destination_venue = offerers_models.Venue.query.filter(
                offerers_models.Venue.id == destination_venue_id
            ).one()
            destination_venue_is_invalid = check_destination_venue_compatibility(origine_venue, destination_venue)
        except sqla_exc.NoResultFound:
            logger.info("Venue not found. Orgine id: %d, destination id: %d", origine_venue_id, destination_venue_id)
            destination_venue_is_invalid = (origine_venue_id, destination_venue_id, "Venue not found")
        if destination_venue_is_invalid:
            invalid_venues.append(destination_venue_is_invalid)
    extract_invalid_venues_to_csv(invalid_venues)


if __name__ == "__main__":
    app.app_context().push()

    main()
    logger.info("Finished")
