"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=cnormant/pc-41731 \
  -f NAMESPACE=fix_offers_withdrawals_for_some_products \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi import settings
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


def main(apply: bool = False) -> None:
    # SUPPORT PHYSIQUE MUSIQUE CD
    # SUPPORT PHYSIQUE MUSIQUE VINYLE
    CSV = "src/pcapi/scripts/fix_offers_withdrawals_for_some_products/offer_ids_physical_with_withdrawal_cd"
    with open(CSV, "r") as csv_file:
        offer_ids = csv_file.read().splitlines()
        for offer_id in offer_ids:
            db.session.query(Offer).filter(Offer.id == offer_id).update(
                {"withdrawalType": None},
                synchronize_session=False,
            )
            if apply:
                db.session.commit()
            else:
                db.session.rollback()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with atomic():
        db.session.execute(sa.text("SET SESSION lock_timeout = :lock_timeout").bindparams(lock_timeout="5s"))
        db.session.execute(
            sa.text("SET SESSION statement_timeout = :statement_timeout").bindparams(statement_timeout="120s")
        )
        main(apply=args.apply)
        db.session.execute(
            sa.text("SET SESSION lock_timeout = ':lock_timeout'").bindparams(
                lock_timeout=settings.DATABASE_LOCK_TIMEOUT
            )
        )
        db.session.execute(
            sa.text("SET SESSION statement_timeout = ':statement_timeout'").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
            )
        )

        if not args.apply:
            logger.info("Finished dry run")
        else:
            logger.info("Finished")
