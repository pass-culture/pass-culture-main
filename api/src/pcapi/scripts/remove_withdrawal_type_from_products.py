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
import sqlalchemy.exc as sa_exc

from pcapi import settings
from pcapi.core.categories import subcategories
from pcapi.core.offers.api import batch_update_offers
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


def main(apply: bool = False) -> None:
    LOADED_SUBCATEGORIES = [
        subcategories.LIVRE_PAPIER.id,
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    ]
    NON_EVENT_SUBCATEGORIES = [
        subcategory.id
        for subcategory in subcategories.ALL_SUBCATEGORIES
        if not subcategory.is_event and subcategory.is_selectable and subcategory.id not in LOADED_SUBCATEGORIES
    ]

    offers_query = db.session.query(Offer).filter(Offer.withdrawalType.is_not(None))

    for subcategory_id in NON_EVENT_SUBCATEGORIES:
        # trying subcategory by subcategory id, to avoid timeout
        logger.info("Updating withdrawalType for subcategory %s", subcategory_id)
        try:
            updated_ids = batch_update_offers(
                offers_query.filter(Offer.subcategoryId == subcategory_id),
                {"withdrawalType": None},
                chunk_size=100,
                apply=apply,
            )
            logger.info("Updated %s offers", len(updated_ids))
        except sa_exc.OperationalError as e:
            db.session.rollback()
            logger.error("Error while updating offers for subcategory %s", subcategory_id, exc_info=e)


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
