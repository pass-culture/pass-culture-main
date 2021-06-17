import logging

from algoliasearch.exceptions import AlgoliaException
from redis import Redis
from redis.client import Pipeline

from pcapi.algolia.infrastructure.api import add_objects
from pcapi.algolia.infrastructure.api import delete_objects
from pcapi.algolia.infrastructure.builder import build_object
from pcapi.connectors.redis import add_offer_ids_in_error
from pcapi.connectors.redis import add_to_indexed_offers
from pcapi.connectors.redis import check_offer_exists
from pcapi.connectors.redis import delete_indexed_offers
from pcapi.repository import offer_queries


logger = logging.getLogger(__name__)


def process_eligible_offers(client: Redis, offer_ids: list[int]) -> None:
    offers_to_add = []
    offers_to_delete = []
    pipeline = client.pipeline()

    offers = offer_queries.get_offers_by_ids(offer_ids)
    for offer in offers:
        if offer and offer.isBookable:
            offers_to_add.append(build_object(offer=offer))
            add_to_indexed_offers(pipeline=pipeline, offer_id=offer.id)
        elif check_offer_exists(client=client, offer_id=offer.id):
            offers_to_delete.append(offer.id)
        else:
            # FIXME (dbaty, 2021-06-14). I think we could safely do
            # without the hashmap in Redis. Check the logs and see if
            # I am right!
            logger.info("Redis 'indexed_offers' hashmap/set saved use from an unnecessary request to Algolia")

    if len(offers_to_add) > 0:
        _process_adding(pipeline=pipeline, client=client, offer_ids=offer_ids, adding_objects=offers_to_add)

    if len(offers_to_delete) > 0:
        _process_deleting(client=client, offer_ids_to_delete=offers_to_delete)

    if not (offers_to_add or offers_to_delete):
        logger.info("[ALGOLIA] no objects were added nor deleted!")


def delete_expired_offers(client: Redis, offer_ids: list[int]) -> None:
    offer_ids_to_delete = []
    for offer_id in offer_ids:
        offer_exists = check_offer_exists(client=client, offer_id=offer_id)

        if offer_exists:
            offer_ids_to_delete.append(offer_id)

    if len(offer_ids_to_delete) > 0:
        _process_deleting(client=client, offer_ids_to_delete=offer_ids_to_delete)


def _process_adding(pipeline: Pipeline, client: Redis, offer_ids: list[int], adding_objects: list[dict]) -> None:
    try:
        add_objects(objects=adding_objects)
        logger.info("[ALGOLIA] %i objects were indexed!", len(adding_objects))
        pipeline.execute()
        pipeline.reset()
    except AlgoliaException as error:
        logger.exception("[ALGOLIA] error when adding objects %s", error)
        add_offer_ids_in_error(client=client, offer_ids=offer_ids)
        pipeline.reset()


def _process_deleting(client: Redis, offer_ids_to_delete: list[int]) -> None:
    try:
        delete_objects(object_ids=offer_ids_to_delete)
        delete_indexed_offers(client=client, offer_ids=offer_ids_to_delete)
        logger.info("[ALGOLIA] %i objects were deleted from index!", len(offer_ids_to_delete))
    except AlgoliaException as error:
        logger.exception("[ALGOLIA] error when deleting objects %s", error)
        add_offer_ids_in_error(client=client, offer_ids=offer_ids_to_delete)
