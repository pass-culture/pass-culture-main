"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/tcoudray-pass/PC-37073-reindexe-missing-offers/api/src/pcapi/scripts/reindex_missing_ean_offers/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core import search
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(start_id: int, end_id: int, batch_size: int) -> None:
    from_id = start_id
    to_id = start_id + batch_size

    while from_id <= end_id:
        offers = db.session.query(offers_models.Offer).filter(
            offers_models.Offer.id.between(from_id, to_id),
            offers_models.Offer.lastProviderId.is_not(None),
        )
        search.async_index_offer_ids([offer.id for offer in offers], search.IndexationReason.OFFER_REINDEXATION)
        from_id = to_id + 1
        to_id = from_id + batch_size


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--start-id", type=int, default=0, help="starting offer id")
    parser.add_argument("--end-id", type=int, default=0, help="ending offer id")
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()

    main(start_id=args.start_id, end_id=args.end_id, batch_size=args.batch_size)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
