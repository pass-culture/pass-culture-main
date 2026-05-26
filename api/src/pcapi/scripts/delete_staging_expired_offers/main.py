"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-42028-delete-staging-expired-offers \
  -f NAMESPACE=delete_staging_expired_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from pcapi import settings
from pcapi.core.offers.repository import get_expired_offer_ids
from pcapi.core.search import unindex_offer_ids


logger = logging.getLogger(__name__)


def main(start_time: datetime.datetime, end_time: datetime.datetime, apply: bool = False) -> None:
    """
    Code from `unindex_expired_offers` here with custom `start_time` and `end_time`
    """

    page = 0
    limit = settings.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE
    while True:
        offer_ids = get_expired_offer_ids(start_time, end_time, offset=page * limit, limit=limit)
        if not offer_ids:
            break

        logger.info("[ALGOLIA] Found %d expired offers to unindex", len(offer_ids))
        if apply:
            unindex_offer_ids(offer_ids)

        page += 1


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    start_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    default_start_time = start_of_day - datetime.timedelta(days=30)
    default_end_time = start_of_day

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--start-time", type=datetime.datetime.fromisoformat, default=default_start_time)
    parser.add_argument("--end-time", type=datetime.datetime.fromisoformat, default=default_end_time)
    args = parser.parse_args()

    main(args.start_time, args.end_time, args.apply)
