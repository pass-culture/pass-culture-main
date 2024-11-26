import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offer-type", type=str, choices=["template", "bookable"], required=True)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"{namespace_dir}/emails.csv"

    offer_class: type[educational_models.CollectiveOfferTemplate | educational_models.CollectiveOffer]
    if args.offer_type == "template":
        offer_class = educational_models.CollectiveOfferTemplate
    elif args.offer_type == "bookable":
        offer_class = educational_models.CollectiveOffer
    else:
        raise ValueError(f"Unkown offer type {args.offer_type}")

    email_data_by_id: dict[int, typing.Any] = {}
    # for each offer id, we store
    # "booking_emails" with the list of invalid emails to remove
    # "valid_emails" with the list of valid emails to add instead
    # (one offer can have several invalid emails)
    with open(file_path, "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")

        for row in csv_rows:
            offer_id = int(row["id"])
            booking_email = row["booking_email"]
            valid_email = row["valid_email"]

            email_data_by_id.setdefault(offer_id, {"booking_emails": [], "valid_emails": []})
            email_data_by_id[offer_id]["booking_emails"].append(booking_email)
            email_data_by_id[offer_id]["valid_emails"].append(valid_email)

    logger.info("Found %s offers to fix", len(email_data_by_id))

    for offer_id, email_data in email_data_by_id.items():
        offer = offer_class.query.filter(offer_class.id == offer_id).one()
        invalid_emails = set(email_data["booking_emails"])
        valid_emails = email_data["valid_emails"]

        if not invalid_emails.issubset(set(offer.bookingEmails)):
            raise ValueError(f"Offer with id {offer_id} does not have expected emails")

        new_booking_emails = [email for email in offer.bookingEmails if email not in invalid_emails]
        new_booking_emails.extend(valid_emails)

        offer.bookingEmails = new_booking_emails
        db.session.add(offer)

    if args.not_dry:
        logger.info("Finished correcting emails")
        db.session.commit()
    else:
        logger.info("Finished dry run for correcting emails, rollback")
        db.session.rollback()
