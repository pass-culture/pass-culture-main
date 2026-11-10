"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=prd \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-44534-fix-settlements-amount \
  -f NAMESPACE=fix_settlements_amount \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    settlements = (
        db.session.query(finance_models.Settlement).options(sa_orm.joinedload(finance_models.Settlement.invoices)).all()
    )

    counter = 0

    for settlement in settlements:
        invoices_amount = sum(invoice.amount for invoice in settlement.invoices)
        if settlement.amount != invoices_amount:
            logger.info(
                "Updating settlement.amount",
                extra={
                    "settlement_id": settlement.id,
                    "old_amount": str(settlement.amount),
                    "new_amount": str(invoices_amount),
                },
            )
            settlement.amount = invoices_amount
            counter += 1

    logger.info("%s settlements updated")


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
