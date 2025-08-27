"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/BSR-cancel-broken-finance-event/api/src/pcapi/scripts/cancel_finance_event/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    finance_event = (
        db.session.query(finance_models.FinanceEvent).filter(finance_models.FinanceEvent.id == 45547663).one_or_none()
    )
    if finance_event:
        finance_event.status = finance_models.FinanceEventStatus.CANCELLED
    db.session.add(finance_event)


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
