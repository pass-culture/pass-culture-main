"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-38854-detach_refused_bank_accounts \
  -f NAMESPACE=detach_refused_bank_accounts \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def main() -> None:
    bank_accounts = (
        db.session.query(finance_models.BankAccount)
        .join(finance_models.BankAccount.venueLinks)
        .filter(
            finance_models.BankAccount.status.in_(
                [
                    finance_models.BankAccountApplicationStatus.WITHOUT_CONTINUATION,
                    finance_models.BankAccountApplicationStatus.REFUSED,
                ]
            ),
            offerers_models.VenueBankAccountLink.timespan.contains(date_utils.get_naive_utc_now()),
        )
        .options(sa_orm.contains_eager(finance_models.BankAccount.venueLinks))
        .all()
    )

    logger.info("Found %d bank accounts to detach", len(bank_accounts))

    for bank_account in bank_accounts:
        logger.info("Bank account ID: %d, Venue ID: %d", bank_account.id, bank_account.venueLinks[0].venueId)
        finance_api.deprecate_venue_bank_account_links(bank_account)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
