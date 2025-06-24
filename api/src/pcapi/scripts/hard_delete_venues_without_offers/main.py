"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-35670-hard-delete-venues-without-offers/api/src/pcapi/scripts/hard_delete_venues_without_offers/main.py

"""

import argparse
import csv
import datetime
import logging
import os
import typing

from sqlalchemy import exc as sa_exc

from pcapi.app import app
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.offerers import exceptions
from pcapi.core.offerers.api import delete_venue
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "Venue ID"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _check_venue_can_be_hard_deleted(venue_id: int, invalid_venues: list[tuple[int, str]]) -> bool:
    venue: Venue = db.session.query(Venue).filter_by(id=venue_id).one_or_none()
    if not venue:
        invalid_venues.append((venue_id, "Venue not found"))
        return False

    six_month_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30 * 6)
    if (
        venue.isPermanent
        or venue.isOpenToPublic
        or venue.siret
        or venue.has_collective_offers
        or venue.hasOffers
        or venue.dateCreated >= six_month_ago
        or bool(venue.venueProviders)
        or venue.adageId
        or venue.criteria
    ):
        invalid_venues.append((venue_id, "Venue can't be deleted"))
        return False
    return True


def _write_invalid_venues_to_csv(invalid_venues: list[tuple[int, str]]) -> None:
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/venues_that_cant_be_hard_deleted.csv"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([VENUE_ID_HEADER, "Reason"])
        writer.writerows(invalid_venues)


def _delete_venues_from_csv(filename: str) -> list[str]:
    invalid_venues: list[tuple[int, str]] = []
    venue_booking_emails = list()
    venue_query = db.session.query(Venue)
    rows = _read_csv_file(filename)
    for row in rows:
        venue_id = int(row[VENUE_ID_HEADER])
        if _check_venue_can_be_hard_deleted(venue_id, invalid_venues):
            venue_booking_email = venue_query.filter_by(id=venue_id).with_entities(Venue.bookingEmail).scalar()
            try:
                delete_venue(venue_id)
                venue_booking_emails.append(venue_booking_email)
            except sa_exc.SQLAlchemyError as error:
                invalid_venues.append((venue_id, "SQL error: " + str(error)))
            except exceptions.CannotDeleteVenueWithBookingsException:
                invalid_venues.append((venue_id, "Can't delete venue with bookings: "))
            except exceptions.CannotDeleteVenueUsedAsPricingPointException:
                invalid_venues.append((venue_id, "Can't delete venue used as pricing point: "))
            except exceptions.CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule:
                invalid_venues.append((venue_id, "Can't delete venue with custom reimbursment rule: "))
    _write_invalid_venues_to_csv(invalid_venues)
    return venue_booking_emails


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    filename = "venues_to_delete"

    with atomic():
        venue_booking_emails = _delete_venues_from_csv(filename)
        if args.not_dry:
            for email in venue_booking_emails:
                external_attributes_api.update_external_pro(email)
            logger.info("Finished")
            db.session.flush()
        else:
            logger.info("Finished dry run, rollback")
            mark_transaction_as_invalid()
