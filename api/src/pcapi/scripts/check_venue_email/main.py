"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=script-check-emails \
  -f NAMESPACE=check-venue-email \
  -f SCRIPT_ARGUMENTS="";

"""

import csv
import logging
import os

from pcapi.app import app
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.schemas import VenueBookingEmail
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    # implement your script here
    failed_email_check: list[tuple[int, str]] = []

    for venue in db.session.query(Venue).filter(Venue.bookingEmail.is_not(None)).yield_per(1_000):
        venue_booking_email = venue.bookingEmail or ""  # helps mypy
        try:
            VenueBookingEmail.validate(venue_booking_email)
        except Exception:
            failed_email_check.append((venue.id, venue_booking_email))

    if failed_email_check:
        logger.info(f"Total invalid emails: {len(failed_email_check)}")
        logger.info("Venues with invalid booking email (venue_id, email):")
        for venue_id, email in failed_email_check:
            logger.info(f"{venue_id}, {email}")

        output_file = f"{os.environ['OUTPUT_DIRECTORY']}/venues_with_invalid_emails.csv"
        logger.info("Exporting data to %s", output_file)

        with open(output_file, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["venue_id", "booking_email"])
            for venue_id, email in failed_email_check:
                writer.writerow([venue_id, email])
    else:
        logger.info("All venue booking emails are valid.")


if __name__ == "__main__":
    app.app_context().push()
    main()
    logger.info("Finished")
