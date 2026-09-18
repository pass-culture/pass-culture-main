"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=tcoudray-pass/PC-43766-add-missing-IN_APP-script \
  -f NAMESPACE=add-missing-IN_APP \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    db.session.query(offers_models.Offer).filter(
        offers_models.Offer.lastProviderId.in_([1075, 2158]),
        offers_models.Offer.subcategoryId == "SEANCE_CINE",
        offers_models.Offer.productId.is_not(None),
        offers_models.Offer.dateCreated >= datetime.datetime(2026, 6, 15),
        offers_models.Offer.withdrawalType.is_(None),
    ).update(
        {"withdrawalType": offers_models.WithdrawalTypeEnum.IN_APP},
        synchronize_session=False,
    )


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
