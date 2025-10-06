"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-38117-script-add-venue-bank-account/api/src/pcapi/scripts/add_venue_bank_account_from_pricing_point/main.py

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

ORIGIN_VENUE_ID_HEADER = "origin_venue_id"


def _get_rows() -> typing.Iterator[dict]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/bank_accounts_update.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        logger.info("Dry run mode enabled, no changes will be made to the database")
        mark_transaction_as_invalid()
    for row in _get_rows():
        origin_venue_id = int(row[ORIGIN_VENUE_ID_HEADER])
        logger.info("Starting to update bank account for venue %d", origin_venue_id)

        origin_venue = (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == origin_venue_id).one_or_none()
        )
        if origin_venue is None:
            logger.info("Origin venue not found. id: %d", origin_venue_id)
            continue
        elif origin_venue.current_pricing_point is None:
            logger.info("Pricing point not found for venue id: %d", origin_venue_id)
            continue
        elif origin_venue.current_pricing_point.current_bank_account is None:
            logger.info("No bank account found for pricing point %d", origin_venue.current_pricing_point.id)
            continue
        elif origin_venue.current_bank_account is not None:
            logger.info(
                "Origin venue already has a bank account. origin_venue_id: %d, bank_account_id: %d",
                origin_venue.id,
                origin_venue.current_bank_account.id,
            )
            continue

        assert origin_venue  # helps mypy
        link = offerers_models.VenueBankAccountLink(
            bankAccount=origin_venue.current_pricing_point.current_bank_account,
            venue=origin_venue,
            timespan=(get_naive_utc_now(),),
        )
        logger.info(
            "Ajout du compte bancaire %d pour la venue %d",
            origin_venue.current_pricing_point.current_bank_account.id,
            origin_venue.id,
        )
        action_history = history_models.ActionHistory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            venue=origin_venue,
            bankAccount=origin_venue.current_pricing_point.current_bank_account,
        )
        db.session.add_all((link, action_history))


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        db.session.commit()
        logger.info("Finished")
    else:
        logger.info("Finished dry run, rollback")
