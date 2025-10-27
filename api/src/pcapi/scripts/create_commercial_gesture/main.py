"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=master   -f NAMESPACE=create_commercial_gesture   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import create_finance_commercial_gesture
from pcapi.core.users import repository as users_repository
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(token: str, author_email: str) -> None:
    booking = (
        db.session.query(bookings_models.Booking)
        .filter(
            bookings_models.Booking.token == token,
            bookings_models.Booking.status == bookings_models.BookingStatus.CANCELLED,
        )
        .one()
    )

    bo_user = users_repository.find_user_by_email(author_email)
    if not bo_user or not bo_user.backoffice_profile:
        raise Exception("wrong author email")

    create_finance_commercial_gesture(
        bookings=[booking],
        amount=booking.total_amount,
        author=bo_user,
        origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
        comment="PC-38543 - Geste commercial exceptionnel suite à retrait d'une réservation faite dans une autre structure",
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--author-email", type=str, required=True)
    args = parser.parse_args()

    main(token=args.token, author_email=args.author_email)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
