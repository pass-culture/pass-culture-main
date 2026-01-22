"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=fix_offer_withdrawal_type \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import os

from pcapi.app import app
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/offers_ids.txt", encoding="utf-8") as f:
        offer_ids = f.readlines()
        for offer_id in offer_ids:
            offer = db.session.query(Offer).filter(Offer.id == int(offer_id)).one()
            offer.withdrawalType = WithdrawalTypeEnum.IN_APP
            db.session.flush()


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
