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

import pcapi.utils.db as db_utils
from pcapi.app import app
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


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


def _get_venue_with_siret(offerer_id: int) -> Venue:
    return (
        db.session.query(Venue).filter(Venue.managingOffererId == offerer_id, Venue.siret.is_not(None)).one()
    )  # should fail script if wrong, as it means input is not up to date


def _add_action_history(venue_bank_account_link: VenueBankAccountLink) -> None:
    history_api.add_action(
        venue=venue_bank_account_link.venue,
        author=None,
        action_type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
        bank_account=venue_bank_account_link.bankAccount,
        comment="Compte bancaire du partenaire culturel mis à jour (PC-37091)",
    )


def _create_bank_account_link(venue: Venue, bank_account: BankAccount) -> None:
    # If venue already has a bank account, but it is different than the offerer's active one
    if venue.current_bank_account_link and venue.current_bank_account_link.bankAccountId != bank_account.id:
        # we close the old one
        venue.current_bank_account_link.timespan = db_utils.make_timerange(
            venue.current_bank_account_link.timespan.lower, datetime.utcnow()
        )
        venue_bank_account_link = VenueBankAccountLink(
            venue=venue, bankAccount=bank_account, timespan=(datetime.utcnow(),)
        )
        logger.info("Updated existing bank account link for venue %s", venue.id)

    # If venue already has no bank account, we add link
    elif not venue.current_bank_account_link:
        venue_bank_account_link = VenueBankAccountLink(
            venue=venue, bankAccount=bank_account, timespan=(datetime.utcnow(),)
        )
    # Venue is already linked to the appropriate bank account
    else:
        logger.info("Venue %s already linked to bank account %s", venue.id, bank_account.id)
        venue_bank_account_link = None

    if venue_bank_account_link:
        db.session.add(venue_bank_account_link)
        _add_action_history(venue_bank_account_link)
        db.session.flush()
        db.session.refresh(venue_bank_account_link)
        logger.info("Added new link for bank account %s on venue %s", bank_account.id, venue.id)


@atomic()
def main(not_dry: bool, filename: str) -> None:
    rows = _read_csv_file(filename)
    logger.info("Reading file %s", filename)
    venue_ids = {int(row[VENUE_ID_HEADER]) for row in rows}
    venue_list: list[Venue] = db.session.query(Venue).filter(Venue.id.in_(venue_ids)).all()
    for venue in venue_list:
        try:
            with atomic():
                bank_account_id = None
                bank_account = _get_offerer_active_bank_account(venue.managingOffererId)

                if not bank_account:
                    logger.info("No valid bank account found on offerer %s", venue.managingOffererId)
                    continue

                else:
                    bank_account_id = bank_account.id
                    venue_with_siret = _get_venue_with_siret(venue.managingOffererId)
                    # add link to active offerer's bank account on venue with siret
                    _create_bank_account_link(venue_with_siret, bank_account)
                    # add link to active offerer's bank account on venue to regularize
                    _create_bank_account_link(venue, bank_account)

        except TypeError:
            logger.error("There has been an error when creating venue bank account link for venue %s", venue.id)
        except sa_exc.IntegrityError:
            logger.error("Link for bank account %s on venue %s already exists", bank_account_id, venue.id)

    if not_dry:
        logger.info("Finished")
    else:
        logger.info("Finished dry run, rollback")
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    filename = "missing_bank_account_on_siret"

    main(not_dry=args.not_dry, filename=filename)
