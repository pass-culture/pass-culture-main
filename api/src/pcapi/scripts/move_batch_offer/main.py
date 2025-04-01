"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-35283-move-offer-batch-check-venue/api/src/pcapi/scripts/move_batch_offer/main.py

"""

import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository


logger = logging.getLogger(__name__)

ORIGIN_VENUE_ID_HEADER = "origin_venue_id"
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
        writer.writerow([ORIGIN_VENUE_ID_HEADER, DESTINATION_VENUE_ID_HEADER, "Reason"])
        writer.writerows(invalid_venues)


def check_destination_venue_validity(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> str | None:
    venues_choices = offerers_repository.get_offerers_venues_with_pricing_point(
        origin_venue,
        include_without_pricing_points=True,
        only_similar_pricing_points=True,
        filter_same_bank_account=True,
    )
    if not venues_choices:
        logger.info(
            "No compatible venue was found for venue %d. Destination venue was %d",
            origin_venue.id,
            destination_venue.id,
        )
        return "No compatible venue. "
    if destination_venue not in venues_choices:
        logger.info("Destination venue %d is not valid for venue %d", destination_venue.id, origin_venue.id)
        return "Destination venue not valid. "
    return None


def check_origin_venue_validity(origin_venue: offerers_models.Venue) -> bool:
    return origin_venue.isPermanent or origin_venue.isOpenToPublic or bool(origin_venue.siret)


def main() -> None:
    invalid_venues = []
    for row in get_venues_to_move_from_csv_file():
        origin_venue_id = int(row[ORIGIN_VENUE_ID_HEADER])
        destination_venue_id = int(row[DESTINATION_VENUE_ID_HEADER])
        invalidity_reason = ""

        origin_venue = offerers_models.Venue.query.filter(offerers_models.Venue.id == origin_venue_id).one_or_none()
        if origin_venue is None:
            logger.info("Origin venue not found. id: %d", origin_venue_id)
            invalidity_reason += "Origin venue not found. "
        else:
            origin_venue_is_invalid = check_origin_venue_validity(origin_venue)
            if origin_venue_is_invalid:
                invalidity_reason += "Origin venue permanent, open to public, with SIRET or pricing point. "

        destination_venue = offerers_models.Venue.query.filter(
            offerers_models.Venue.id == destination_venue_id
        ).one_or_none()
        if destination_venue is None:
            logger.info("Destination venue not found. id: %d", destination_venue_id)
            invalidity_reason += "Destination venue not found. "
        elif origin_venue:
            destination_venue_is_invalid = check_destination_venue_validity(origin_venue, destination_venue)
            if destination_venue_is_invalid:
                invalidity_reason += destination_venue_is_invalid

        if invalidity_reason:
            invalid_venues.append((origin_venue_id, destination_venue_id, invalidity_reason))
    extract_invalid_venues_to_csv(invalid_venues)


if __name__ == "__main__":
    app.app_context().push()

    main()
    logger.info("Finished")
