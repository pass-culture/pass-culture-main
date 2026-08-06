"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=tcoudray-pass/PC-42792-script-cinegestion \
  -f NAMESPACE=validate_cinegestion_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from functools import partial

from pcapi.core import search
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)


def main() -> None:
    """This script does 1 thing : finalizing offer"""
    offers_to_validate = (
        db.session.query(offers_models.Offer)
        .filter(
            offers_models.Offer.lastProviderId == 1075,
            offers_models.Offer.publicationDatetime == None,
        )
        .all()
    )
    logger.info("[CineGestion - Fix] Offers count: %i", len(offers_to_validate))

    for offer in offers_to_validate:
        now = date_utils.get_naive_utc_now()
        offer.finalizationDatetime = now
        offer.publicationDatetime = now

        on_commit(
            partial(search.async_index_offer_ids, [offer.id], reason=offers_api.IndexationReason.OFFER_PUBLICATION)
        )
        on_commit(
            partial(
                logger.info,
                "Offer has been published",
                extra={"offer_id": offer.id, "venue_id": offer.venueId},
                technical_message_id="offer.published",
            )
        )

        logger.info("[CineGestion - Fix] Offer published (id=%i)", offer.id)

    db.session.flush()


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
