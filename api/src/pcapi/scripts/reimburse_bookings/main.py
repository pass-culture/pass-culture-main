"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40800-support-actions \
  -f NAMESPACE=reimburse_bookings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
from typing import Sequence

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.bookings.models import Booking
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)
namespace_dir = os.path.dirname(os.path.abspath(__file__))

FILE_NAME = "users_to_reimburse.csv"


def reimburse_booking(booking_to_reimburse: Booking) -> None:
    user = booking_to_reimburse.user

    deposit = user.deposit
    if not deposit:
        logger.error("no deposit was found", extra={"user_id": user.id, "booking_token": booking_to_reimburse.token})
        return

    recredit = Recredit(
        deposit=deposit,
        amount=booking_to_reimburse.total_amount,
        recreditType=RecreditType.MANUAL_MODIFICATION,
        comment=f"(PC-40800) Remboursement de la réservation {booking_to_reimburse.token} qui n'a pas pu être consommée à cause d'un incident technique",
    )
    deposit.amount += recredit.amount
    db.session.add(recredit)

    logger.info(
        "Reimbursed booking",
        extra={"user_id": user.id, "booking_token": booking_to_reimburse.token, "amount": recredit.amount},
    )


def read_bookings_from_csv(file_name: str) -> Sequence[Booking]:
    with open(f"{namespace_dir}/{file_name}", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return db.session.scalars(
            select(Booking).where(Booking.token.in_([row["token"].upper() for row in reader]))
        ).all()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--author-id", type=int, default=None)
    args = parser.parse_args()

    with atomic():
        if not args.apply:
            mark_transaction_as_invalid()
            logger.info("dry run, rollbacking at the end of the transaction")

        for booking_to_reimburse in read_bookings_from_csv(FILE_NAME):
            reimburse_booking(booking_to_reimburse)

            if args.apply:
                update_external_user(booking_to_reimburse.user)
