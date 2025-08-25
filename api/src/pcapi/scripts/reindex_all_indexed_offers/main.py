"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-37564-reindex-all-indexed-offers/api/src/pcapi/scripts/reindex_all_indexed_offers/main.py

"""

import argparse
import logging
import time

from flask import current_app
from redis.client import Redis

from pcapi.app import app
from pcapi.core.search import reindex_offer_ids
from pcapi.core.search.redis_queues import REDIS_HASHMAP_INDEXED_OFFERS_NAME
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def main(indexing_batch_size: int = 1_000) -> None:
    redis_client: Redis = current_app.redis_client
    offer_ids_iterator = redis_client.hscan_iter(name=REDIS_HASHMAP_INDEXED_OFFERS_NAME, count=10_000)
    nb_offers_to_reindex = redis_client.hlen(REDIS_HASHMAP_INDEXED_OFFERS_NAME)
    logger.info("%d offers to reindex", nb_offers_to_reindex)

    total_reindexed_offers = 0
    start_time = time.time()
    for chunk in get_chunks(offer_ids_iterator, chunk_size=indexing_batch_size):
        offer_ids = [offer_id for offer_id, _ in chunk]
        reindex_offer_ids(offer_ids)
        total_reindexed_offers += len(offer_ids)
        logger.info(
            "%d / %d (%.2f%%) in %.2fs",
            total_reindexed_offers,
            nb_offers_to_reindex,
            total_reindexed_offers * 100 / nb_offers_to_reindex,
            time.time() - start_time,
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=1_000)
    args = parser.parse_args()

    main(indexing_batch_size=args.batch_size)

    logger.info("Finished")
