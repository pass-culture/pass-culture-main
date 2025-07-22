"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-37159-add-ba-on-venues-without-siret/api/src/pcapi/scripts/add_bank_account_on_venue_without_siret/main.py

"""

import argparse
import csv
import logging
import os
import typing
from datetime import datetime

from pcapi.app import app
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


VENUE_ID_HEADER = "initial_venue_id"
BANK_ACCOUNT_ID_HEADER = "bank_account_id"

logger = logging.getLogger(__name__)


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


@atomic()
def _create_venue_bank_account_link(venue: Venue, bank_account: BankAccount, check_iban: bool) -> None:
    current_link = venue.current_bank_account_link

    if current_link:
        current_link.timespan.upper = datetime.utcnow()

    if check_iban:
        if not current_link:
            logger.error("Pas de compte bancaire associé à la venue d'origine %s", venue.id)
            return

        elif current_link.bankAccount.iban != bank_account.iban:
            logger.error(
                "Les IBANs du compte bancaire associé à la venue d'origine %s et le nouveau compte bancaire %s ne correspondent pas",
                current_link.bankAccount.id,
                bank_account.id,
            )
            return

    if bank_account.status == BankAccountApplicationStatus.ACCEPTED and bank_account.isActive:
        new_link = VenueBankAccountLink(venue=venue, bankAccount=bank_account, timespan=(datetime.utcnow(),))
        db.session.add(new_link)
        logger.info("VenueBankAccountLink créé pour la venue %s avec le compte bancaire %s", venue.id, bank_account.id)
    else:
        logger.error("Le compte bancaire %s ne peut pas être associé à la venue %s", bank_account.id, venue.id)


@atomic()
def main(not_dry: bool, check_iban: bool, filename: str) -> None:
    rows = _read_csv_file(filename)
    logger.info("Reading file %s", filename)

    venue_bank_account_pairs = [(int(row[VENUE_ID_HEADER]), int(row[BANK_ACCOUNT_ID_HEADER])) for row in rows]
    venue_ids = {venue_id for venue_id, _ in venue_bank_account_pairs}
    bank_account_ids = {bank_account_id for _, bank_account_id in venue_bank_account_pairs}

    venues: list[Venue] = db.session.query(Venue).filter(Venue.id.in_(venue_ids)).all()
    venue_by_id = {venue.id: venue for venue in venues}

    bank_accounts: list[BankAccount] = db.session.query(BankAccount).filter(BankAccount.id.in_(bank_account_ids)).all()
    bank_account_by_id = {account.id: account for account in bank_accounts}

    venue_bank_accounts = [
        (venue_by_id[venue_id], bank_account_by_id[bank_account_id])
        for venue_id, bank_account_id in venue_bank_account_pairs
    ]

    for venue, bank_account in venue_bank_accounts:
        _create_venue_bank_account_link(venue=venue, bank_account=bank_account, check_iban=check_iban)

    if not not_dry:
        logger.info("Finished dry run, rollback")
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--check-iban", action="store_true")
    args = parser.parse_args()

    filename = "missing_bank_account_on_venues"

    main(not_dry=args.not_dry, check_iban=args.check_iban, filename=filename)

    if args.not_dry:
        logger.info("Finished")
