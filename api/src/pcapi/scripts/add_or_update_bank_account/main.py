"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-37159-add-bank-account-to-venues/api/src/pcapi/scripts/add_or_update_bank_account/main.py

"""

import argparse
import csv
import logging
import os
import typing
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import exc as sa_exc

import pcapi.utils.db as db_utils
from pcapi.app import app
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.core.offerers.models import VenuePricingPointLink
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


VENUE_ID_HEADER = "origin_venue_id"

logger = logging.getLogger(__name__)


def _read_csv_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/venues_bank_account.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _get_bank_account_from_venue_with_siret_and_same_pricing_point_as_origin_venue(
    offerer_id: int, origin_venue_pricing_point_id: int | None, iban: str | None
) -> BankAccount | None:
    query = (
        db.session.query(BankAccount)
        .join(
            VenueBankAccountLink,
            sa.and_(
                VenueBankAccountLink.bankAccountId == BankAccount.id,
                VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .join(Venue, VenueBankAccountLink.venueId == Venue.id)
        .join(
            VenuePricingPointLink,
            sa.and_(
                VenuePricingPointLink.venueId == Venue.id,
                VenuePricingPointLink.timespan.contains(datetime.utcnow()),
            ),
            isouter=True,
        )
        .filter(
            BankAccount.offererId == offerer_id,
            BankAccount.status == BankAccountApplicationStatus.ACCEPTED,
            BankAccount.isActive.is_(True),
            Venue.siret.is_not(None),
            VenuePricingPointLink.pricingPointId == origin_venue_pricing_point_id,
        )
    )
    if iban:
        query = query.filter(BankAccount.iban == iban)
    if query.count() == 1:
        return query.one()
    logger.info("%d active bank account on offerer %s", query.count(), offerer_id)
    return None


def _add_action_history(venue_bank_account_link: VenueBankAccountLink) -> None:
    history_api.add_action(
        venue=venue_bank_account_link.venue,
        author=None,
        action_type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
        bank_account=venue_bank_account_link.bankAccount,
        comment="Compte bancaire du partenaire culturel mis à jour (PC-37159)",
    )


def _create_bank_account_link(venue: Venue, bank_account: BankAccount) -> None:
    if venue.current_bank_account_link:
        # we close the old one bank account
        venue.current_bank_account_link.timespan = db_utils.make_timerange(
            venue.current_bank_account_link.timespan.lower, datetime.utcnow()
        )
    # we add link to the new bank account
    venue_bank_account_link = VenueBankAccountLink(venue=venue, bankAccount=bank_account, timespan=(datetime.utcnow(),))
    logger.info("Updated existing bank account link for venue %s", venue.id)

    db.session.add(venue_bank_account_link)
    _add_action_history(venue_bank_account_link)
    db.session.flush()
    db.session.refresh(venue_bank_account_link)
    logger.info("Added new link for bank account %s on venue %s", bank_account.id, venue.id)


def _get_venue_bank_account_iban_if_exists(venue: Venue) -> str | None:
    if venue.current_bank_account_link:
        return venue.current_bank_account_link.bankAccount.iban
    return None


@atomic()
def main(not_dry: bool) -> None:
    rows = _read_csv_file()
    venue_ids = {int(row[VENUE_ID_HEADER]) for row in rows}
    venue_list: list[Venue] = db.session.query(Venue).filter(Venue.id.in_(venue_ids)).all()
    for venue in venue_list:
        try:
            with atomic():
                iban = _get_venue_bank_account_iban_if_exists(venue)
                bank_account_id = None
                bank_account = _get_bank_account_from_venue_with_siret_and_same_pricing_point_as_origin_venue(
                    venue.managingOffererId, venue.current_pricing_point_id, iban
                )

                if not bank_account:
                    logger.info("No valid bank account found on offerer %s", venue.managingOffererId)
                    continue

                else:
                    bank_account_id = bank_account.id
                    # add link to active offerer's bank account on venue to regularize
                    _create_bank_account_link(venue, bank_account)

        except TypeError:
            logger.info("There has been an error when creating venue bank account link for venue %s", venue.id)
        except sa_exc.IntegrityError:
            logger.info("Link for bank account %s on venue %s already exists", bank_account_id, venue.id)

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

    main(not_dry=args.not_dry)
