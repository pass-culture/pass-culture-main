"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-37091-add-bank-account-on-siret/api/src/pcapi/scripts/add_bank_account_on_venue/main.py

"""

import argparse
import csv
import logging
import os
import typing
from datetime import datetime

from sqlalchemy import exc as sa_exc

from pcapi.app import app
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


VENUE_ID_HEADER = "initial_venue_id"

logger = logging.getLogger(__name__)


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _get_offerer_active_bank_account(offerer_id: int) -> BankAccount | None:
    query = db.session.query(BankAccount).filter(
        BankAccount.offererId == offerer_id,
        BankAccount.status == BankAccountApplicationStatus.ACCEPTED,
        BankAccount.isActive.is_(True),
    )
    if query.count() == 1:
        return query.one()
    logger.info("Not just 1 active bank account on offerer %s", offerer_id)
    return None


@atomic()
def main(not_dry: bool, filename: str) -> None:
    rows = _read_csv_file(filename)
    logger.info("Reading file %s", filename)
    venue_ids = {int(row[VENUE_ID_HEADER]) for row in rows}
    venue_list: list[Venue] = db.session.query(Venue).filter(Venue.id.in_(venue_ids)).all()
    for venue in venue_list:
        if bank_account := _get_offerer_active_bank_account(venue.managingOffererId):
            venue_bank_account_link = VenueBankAccountLink(
                venue=venue, bankAccount=bank_account, timespan=(datetime.utcnow(),)
            )
            db.session.add(venue_bank_account_link)
            try:
                db.session.flush()
                logger.info("Adding link for bank account %s on venue %s", bank_account.id, venue.id)
            except sa_exc.IntegrityError:
                logger.error("Link for bank account %s on venue %s already exists", bank_account.id, venue.id)
                mark_transaction_as_invalid()

    if not not_dry:
        logger.info("Finished dry run, rollback")
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    filename = "missing_bank_account_on_siret"

    main(not_dry=args.not_dry, filename=filename)

    if args.not_dry:
        logger.info("Finished")
