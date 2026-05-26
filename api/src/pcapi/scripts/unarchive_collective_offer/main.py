"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42029-desarchiver-une-offre-reservable \
  -f NAMESPACE=unarchive_collective_offer \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.educational import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(offer_id: int) -> None:
    offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer_id).one()

    status, _, is_archived = offer.get_base_displayed_status()

    if not is_archived:
        raise ValueError("Offer is not archived")

    if status != models.CollectiveOfferDisplayedStatus.BOOKED:
        raise ValueError("Offer would not be booked")

    offer.dateArchived = None
    offer.isActive = True
    db.session.flush()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--offer-id", type=int)
    args = parser.parse_args()

    main(args.offer_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
