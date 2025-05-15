from collections import abc
import contextlib
import datetime
import logging

from flask import current_app
import redis

from pcapi import settings


logger = logging.getLogger(__name__)


REDIS_OFFER_IDS_NAME = "search:algolia:offer-ids:set"
REDIS_OFFER_IDS_IN_ERROR_NAME = "search:algolia:offer-ids-in-error:set"
REDIS_VENUE_IDS_FOR_OFFERS_NAME = "search:algolia:venue-ids-for-offers:set"

REDIS_VENUE_IDS_TO_INDEX = "search:algolia:venue-ids-to-index:set"
REDIS_VENUE_IDS_IN_ERROR_TO_INDEX = "search:algolia:venue-ids-in-error-to-index:set"

REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX = "search:algolia:collective-offer-template-ids-to-index:set"
REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX = (
    "search:algolia:collective-offer-template-ids-in-error-to-index:set"
)
QUEUES = (
    REDIS_OFFER_IDS_NAME,
    REDIS_OFFER_IDS_IN_ERROR_NAME,
    REDIS_VENUE_IDS_FOR_OFFERS_NAME,
    REDIS_VENUE_IDS_TO_INDEX,
    REDIS_VENUE_IDS_IN_ERROR_TO_INDEX,
    REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX,
    REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX,
)
REDIS_HASHMAP_INDEXED_OFFERS_NAME = "indexed_offers"


class AlgoliaIndexingQueuesMixin:
    def __init__(self) -> None:
        self.redis_client = current_app.redis_client
        super().__init__()

    def _can_enqueue_offer_ids(self, offer_ids: abc.Collection[int]) -> bool:
        if settings.ALGOLIA_OFFERS_INDEX_MAX_SIZE < 0:
            return True

        currently_indexed_offers = self.redis_client.hlen(REDIS_HASHMAP_INDEXED_OFFERS_NAME)
        offers_in_indexing_queue = self.redis_client.scard(REDIS_OFFER_IDS_NAME)
        limit = settings.ALGOLIA_OFFERS_INDEX_MAX_SIZE
        can_enqueue = currently_indexed_offers + offers_in_indexing_queue < limit
        if not can_enqueue:
            logger.warning(
                "Exceeded maximum Algolia offer index size",
                extra={
                    "currently_indexed_offers": currently_indexed_offers,
                    "offers_in_indexing_queue": offers_in_indexing_queue,
                    "partial_ids": list(offer_ids)[:50],
                    "count": len(offer_ids),
                    "limit": limit,
                },
            )
        return can_enqueue

    def enqueue_offer_ids(self, offer_ids: abc.Collection[int]) -> None:
        if not self._can_enqueue_offer_ids(offer_ids):
            return

        self._enqueue_ids(offer_ids, REDIS_OFFER_IDS_NAME)

    def enqueue_offer_ids_in_error(self, offer_ids: abc.Collection[int]) -> None:
        self._enqueue_ids(offer_ids, REDIS_OFFER_IDS_IN_ERROR_NAME)

    def enqueue_collective_offer_template_ids(
        self,
        collective_offer_template_ids: abc.Collection[int],
    ) -> None:
        self._enqueue_ids(
            collective_offer_template_ids,
            REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX,
        )

    def enqueue_collective_offer_template_ids_in_error(
        self,
        collective_offer_template_ids: abc.Collection[int],
    ) -> None:
        self._enqueue_ids(
            collective_offer_template_ids,
            REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX,
        )

    def enqueue_venue_ids(self, venue_ids: abc.Collection[int]) -> None:
        return self._enqueue_ids(venue_ids, REDIS_VENUE_IDS_TO_INDEX)

    def enqueue_venue_ids_in_error(self, venue_ids: abc.Collection[int]) -> None:
        return self._enqueue_ids(venue_ids, REDIS_VENUE_IDS_IN_ERROR_TO_INDEX)

    def enqueue_venue_ids_for_offers(self, venue_ids: abc.Collection[int]) -> None:
        return self._enqueue_ids(venue_ids, REDIS_VENUE_IDS_FOR_OFFERS_NAME)

    def _enqueue_ids(self, ids: abc.Collection[int], queue: str) -> None:
        if not ids:
            return

        try:
            self.redis_client.sadd(queue, *ids)
        except redis.exceptions.RedisError:
            logger.exception("Could not add ids to indexation queue", extra={"ids": ids, "queue": queue})

    def pop_offer_ids_from_queue(
        self,
        count: int,
        from_error_queue: bool = False,
    ) -> contextlib.AbstractContextManager:
        if from_error_queue:
            queue = REDIS_OFFER_IDS_IN_ERROR_NAME
        else:
            queue = REDIS_OFFER_IDS_NAME
        return self._pop_ids_from_queue(queue, count)

    def pop_venue_ids_from_queue(
        self,
        count: int,
        from_error_queue: bool = False,
    ) -> contextlib.AbstractContextManager:
        if from_error_queue:
            queue = REDIS_VENUE_IDS_IN_ERROR_TO_INDEX
        else:
            queue = REDIS_VENUE_IDS_TO_INDEX
        return self._pop_ids_from_queue(queue, count)

    def pop_collective_offer_template_ids_from_queue(
        self,
        count: int,
        from_error_queue: bool = False,
    ) -> contextlib.AbstractContextManager:
        if from_error_queue:
            queue = REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX
        else:
            queue = REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX
        return self._pop_ids_from_queue(queue, count)

    def pop_venue_ids_for_offers_from_queue(
        self,
        count: int,
    ) -> contextlib.AbstractContextManager:
        return self._pop_ids_from_queue(REDIS_VENUE_IDS_FOR_OFFERS_NAME, count)

    @contextlib.contextmanager
    def _pop_ids_from_queue(
        self,
        queue: str,
        count: int,
    ) -> abc.Generator[set[int], None, None]:
        """Return a set of int identifiers from the queue, as a
        context manager.

        Processing these identifiers must be done within the returned
        context context. It guarantees that there is no data loss if
        an error (or a complete crash) occurs while processing the
        identifiers.
        """
        # We must pop and not get-and-delete. Otherwise two concurrent
        # cron jobs could delete the wrong offers from the queue:
        # 1. Cron job 1 gets the first 1.000 offers from the queue.
        # 2. Cron job 2 gets the same 1.000 offers from the queue.
        # 3. Cron job 1 finishes processing the batch and deletes the
        #    first 1.000 offers from the queue. OK.
        # 4. Cron job 2 finishes processing the batch and also deletes
        #    the first 1.000 offers from the queue. Not OK, these are
        #    not the same offers it just processed!
        #
        # Also, we cannot "just" use pop. If the Python process
        # crashes between popping and processing ids, we will lose the
        # ids. Possible cause of crash: pod is OOMKilled or recycled,
        # for example. To work around that, items to be processed are
        # moved to a specific queue. This queue is deleted once all
        # items are processed. If a crash happens, the queue is still
        # there. A separate cron job looks for these (specially-named)
        # queues and adds back their items to the originating queue
        # (see `clean_processing_queues`).
        timestamp = datetime.datetime.utcnow().timestamp()
        processing_queue = f"{queue}:processing:{timestamp}"
        try:
            ids = self.redis_client.srandmember(queue, count)
            with self.redis_client.pipeline(transaction=True) as pipeline:
                for id_ in ids:
                    pipeline.smove(queue, processing_queue, id_)
                pipeline.execute()
                batch = {int(id_) for id_ in ids}  # str -> int
                logger.info(
                    "Moved batch of object ids to index to processing queue",
                    extra={
                        "originating_queue": queue,
                        "processing_queue": processing_queue,
                        "requested_count": count,
                        "effective_count": len(batch),
                    },
                )
                yield batch
                self.redis_client.delete(processing_queue)
                logger.info(
                    "Deleted processing queue",
                    extra={
                        "originating_queue": queue,
                        "processing_queue": processing_queue,
                    },
                )
        except redis.exceptions.RedisError:
            logger.exception(
                "Could not pop object ids to index from queue",
                extra={"originating_queue": queue, "processing_queue": processing_queue},
            )
            yield set()

    def count_offers_to_index_from_queue(self, from_error_queue: bool = False) -> int:
        if from_error_queue:
            queue = REDIS_OFFER_IDS_IN_ERROR_NAME
        else:
            queue = REDIS_OFFER_IDS_NAME

        try:
            return self.redis_client.scard(queue)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not count offers left to index from queue")
            return 0

    def check_offer_id_is_indexed(self, offer_id: int) -> bool:
        try:
            return self.redis_client.hexists(
                REDIS_HASHMAP_INDEXED_OFFERS_NAME,
                str(offer_id),
            )
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not check whether offer exists in cache", extra={"offer": offer_id})
            # This function is only used to avoid an unnecessary
            # deletion request to Algolia if the offer is not in the
            # cache. Here we don't know, so we'll say it's in the
            # cache so that we do perform a request to Algolia.
            return True

    def clean_processing_queues(self) -> None:
        """Move items from the processing queue back to the initial queue,
        once a delay has passed and we are reasonably sure that the job
        has crashed (and that the items must be processed again).
        """
        redis_client = current_app.redis_client
        for originating_queue in QUEUES:
            # There a very few queues, no need to paginate with `_cursor`.
            pattern = f"{originating_queue}:processing:*"
            cursor = 0
            while 1:
                cursor, processing_queues = redis_client.scan(cursor, pattern)
                for processing_queue in processing_queues:
                    timestamp = float(processing_queue.rsplit(":")[-1])
                    if timestamp > datetime.datetime.utcnow().timestamp() - 60 * 60:
                        continue  # less than 1 hour ago, too recent, could still be processing
                    self._clean_processing_queue(processing_queue, originating_queue)
                if cursor == 0:  # back to start, we have been through the pagination
                    break

    def _clean_processing_queue(self, processing_queue: str, originating_queue: str) -> None:
        redis_client = current_app.redis_client
        with redis_client.pipeline(transaction=True) as pipeline:
            try:
                for id_ in redis_client.smembers(processing_queue):
                    pipeline.smove(processing_queue, originating_queue, id_)
                pipeline.execute()
            except Exception:
                # That's not critical: the processing queue will
                # still be here, and can be handled in the next run
                # of this function. But we raise a warning because
                # it may denote a problem with our code or with
                # Redis.
                logger.exception(
                    "Failed to handle indexation processing queue: %s (will try again)",
                    processing_queue,
                )
            else:
                logger.info(
                    "Found old processing queue, moved back items to originating queue",
                    extra={"queue": originating_queue, "processing_queue": processing_queue},
                )

    def remove_offer_ids_from_store(self, offer_ids: abc.Collection[int]) -> None:
        try:
            self.redis_client.hdel(
                REDIS_HASHMAP_INDEXED_OFFERS_NAME,
                *(str(offer_id) for offer_id in offer_ids),
            )
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not remove offers from indexed offers set", extra={"offers": offer_ids})

    def remove_all_offers_from_store(self) -> None:
        try:
            self.redis_client.delete(REDIS_HASHMAP_INDEXED_OFFERS_NAME)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not clear indexed offers cache",
            )

    def add_offer_ids_to_store(self, offer_ids: abc.Collection[int]) -> None:
        try:
            # We used to store a summary of each offer, which is why
            # we used hashmap and not a set. But since we don't need
            # the value anymore, we can store the lightest object
            # possible to make Redis use less memory. In the future,
            # we may even remove the hashmap if it's not proven useful
            # (see log in reindex_offer_ids)
            pipeline = self.redis_client.pipeline(transaction=True)
            for offer_id in offer_ids:
                pipeline.hset(REDIS_HASHMAP_INDEXED_OFFERS_NAME, str(offer_id), "")
            pipeline.execute()
        except Exception:
            logger.exception("Could not add to list of indexed offers", extra={"offers": offer_ids})
        finally:
            pipeline.reset()
