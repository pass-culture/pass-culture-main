"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-43774-test-cegid-upgrade \
  -f NAMESPACE=cegid_test_get_settlements \
  -f SCRIPT_ARGUMENTS="";

"""

import datetime
import logging

from pcapi import settings
from pcapi.core.finance.backend import CegidFinanceBackend
from pcapi.models import db


logger = logging.getLogger(__name__)


class CegidSandboxFinanceBackend(CegidFinanceBackend):
    def __init__(self) -> None:
        self._base_url = "https://xrp-flex.cegid.cloud/passculture_sandbox"
        self._interface = settings.CEGID_ENDPOINT


def get_settlements(from_date: datetime.date, to_date: datetime.date) -> None:
    settlement_payloads = CegidSandboxFinanceBackend().get_settlements(from_date, to_date)
    logger.info(
        "get_settlements called",
        extra={
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "count": len(settlement_payloads),
        },
    )
    print(settlement_payloads)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    get_settlements(datetime.date(2026, 8, 16), datetime.date.today())

    logger.info("Finished")
    db.session.rollback()  # do not save anything in database
