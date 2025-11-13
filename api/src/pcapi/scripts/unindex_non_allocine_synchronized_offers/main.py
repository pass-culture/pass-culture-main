"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=unindex_non_allocine_synchronized_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import itertools
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.offers.models import Offer
from pcapi.core.providers.models import Provider
from pcapi.core.search import unindex_offer_ids
from pcapi.core.search.redis_queues import REDIS_HASHMAP_INDEXED_OFFERS_NAME
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    redis_client = app.redis_client
    provider_ids = db.session.scalars(
        sa.select(Provider.id).where(
            Provider.localClass.in_(
                (
                    "BoostStocks",
                    "CGRStocks",
                    "CDSStocks",
                    "EMSStocks",
                )
            )
        )
    ).all()
    for str_offer_ids_batch in itertools.batched(redis_client.hgetall(REDIS_HASHMAP_INDEXED_OFFERS_NAME).keys(), 1000):
        offer_ids = list(map(int, str_offer_ids_batch))
        offer_ids_to_unindex = db.session.scalars(
            sa.select(Offer.id).where(Offer.id.in_(offer_ids), Offer.lastProviderId.in_(provider_ids))
        ).all()
        if not_dry:
            unindex_offer_ids(offer_ids_to_unindex)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
