"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37809-api-10-offerer-avec-1-seul-iban-mais-plusieurs-comptes-bancaires-mettre-le-meme-cb-sur-toutes-les-venues-de-lofferer/api/src/pcapi/scripts/merge_same_iban_in_one_object/main.py

"""

import argparse
import logging
from datetime import datetime

import sqlalchemy.orm as sa_orm

import pcapi.core.offerers.models as offerer_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def merge_iban_for_offerer(offerer_id: int) -> None:
    venues = (
        db.session.query(offerer_models.Venue)
        .join(offerer_models.Venue.bankAccountLinks)
        .filter(
            offerer_models.Venue.managingOffererId == offerer_id,
            offerer_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
        )
        .options(
            sa_orm.joinedload(offerer_models.Venue.bankAccountLinks).joinedload(
                offerer_models.VenueBankAccountLink.bankAccount
            ),
        )
        .all()
    )
    ibans = {venue.current_bank_account.iban for venue in venues}
    if len(ibans) > 1:
        logger.warning(f"Offerer {offerer_id} has {len(ibans)} different IBANs: {ibans}")
        return
    bank_accounts = sorted({venue.current_bank_account for venue in venues}, key=lambda ba: ba.id)
    reference_bank_account = bank_accounts.pop()
    for bank_account in bank_accounts:
        for bank_account_link in list(bank_account.venueLinks):
            bank_account_link.bankAccount = reference_bank_account
            logger.info(
                f"Linking venue {bank_account_link.venue.id} to bank account {reference_bank_account.id} instead of {bank_account.id}"
            )
            db.session.add(bank_account_link)
        db.session.flush()
        db.session.delete(bank_account)
        db.session.flush()
        logger.info(f"Deleting bank account {bank_account.id} with IBAN {bank_account.iban}")


def main(dry_run: bool, offerer_ids: list[int]) -> None:
    for offerer_id in offerer_ids:
        merge_iban_for_offerer(offerer_id)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument(
        "--offerer-ids",
        nargs="+",
        type=int,
        required=True,
        metavar="OFFERER_ID",
        help="List of offerer ids to process",
    )
    args = parser.parse_args()

    main(dry_run=not args.not_dry, offerer_ids=args.offerer_ids)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
