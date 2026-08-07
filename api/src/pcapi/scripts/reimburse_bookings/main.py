"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42024-reimburse-bookings \
  -f NAMESPACE=reimburse_bookings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
import typing

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from pcapi.app import app
from pcapi.core.bookings.models import Booking
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)
namespace_dir = os.path.dirname(os.path.abspath(__file__))


def reimburse_bookings(should_update_external_user: bool) -> None:
    bookings = _read_bookings_from_csv("tokens.csv")
    for booking in bookings:
        _reimburse_booking(booking)

        if should_update_external_user:
            update_external_user(booking.user)


def _read_bookings_from_csv(file_name: str) -> typing.Sequence[Booking]:
    with open(f"{namespace_dir}/{file_name}", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        tokens = [row["token"] for row in reader]

    bookings_query = (
        select(Booking).where(Booking.token.in_(tokens)).options(joinedload(Booking.user).selectinload(User.deposits))
    )
    return db.session.scalars(bookings_query).all()


def _reimburse_booking(booking: Booking) -> None:
    deposit = booking.user.deposit
    if not deposit:
        logger.warning("no deposit found for user %s", booking.user.id)
        return

    recredit = Recredit(
        deposit=deposit,
        amount=booking.quantity * booking.stock.price,
        recreditType=RecreditType.MANUAL_MODIFICATION,
        comment=f"(PC-42024) Remboursement de la contremarque {booking.token}",
    )
    deposit.amount += recredit.amount

    logger.info(f"recredited {recredit.amount} euros to {booking.user = } and {deposit = }")

    db.session.add(recredit)
    db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    reimburse_bookings(should_update_external_user=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
