"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-43774-test-cegid-upgrade \
  -f NAMESPACE=cegid_test_push_ba \
  -f SCRIPT_ARGUMENTS="";

"""

import datetime
import logging
import time

from sqlalchemy import orm as sa_orm

from pcapi import settings
from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend import CegidFinanceBackend
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


class CegidSandboxFinanceBackend(CegidFinanceBackend):
    def __init__(self) -> None:
        self._base_url = "https://xrp-flex.cegid.cloud/passculture_sandbox"
        self._interface = settings.CEGID_ENDPOINT


def push_bank_account(bank_account_id: int) -> dict | None:
    backend = CegidSandboxFinanceBackend()
    bank_account = (
        db.session.query(finance_models.BankAccount)
        .filter_by(id=bank_account_id)
        .options(
            sa_orm.joinedload(finance_models.BankAccount.offerer, innerjoin=True).load_only(
                offerers_models.Offerer.name, offerers_models.Offerer.siren
            )
        )
        .one()
    )
    return backend.push_bank_account(bank_account)


def push_bank_accounts() -> None:
    bank_accounts = (
        db.session.query(finance_models.BankAccount)
        .filter(
            finance_models.BankAccount.dateCreated > datetime.datetime(2026, 9, 5),
            finance_models.BankAccount.status == finance_models.BankAccountApplicationStatus.ACCEPTED,
        )
        .with_entities(finance_models.BankAccount.id)
        .all()
    )

    if not bank_accounts:
        return

    bank_account_ids = [e[0] for e in bank_accounts]
    for bank_account_id in bank_account_ids:
        try:
            logger.info(
                "Push bank account", extra={"bank_account_id": bank_account_id, "backend": "CegidSandboxFinanceBackend"}
            )
            push_bank_account(bank_account_id)
        except Exception as exc:
            logger.exception(
                "Unable to sync bank account",
                extra={
                    "bank_account_id": bank_account_id,
                    "exc": str(exc),
                },
            )
            # Wait until next cron run to continue sync process
            break
        else:
            time_to_sleep = finance_backend.get_time_to_sleep_between_two_sync_requests()
            time.sleep(time_to_sleep)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    push_bank_accounts()

    logger.info("Finished")
    db.session.rollback()  # do not save anything in database
