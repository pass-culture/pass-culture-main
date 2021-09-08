import logging
from typing import Iterable

import algoliasearch.search_client
from flask import current_app
import redis

from pcapi import settings
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import base
import pcapi.utils.date as date_utils
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)

REDIS_LIST_OFFER_IDS_NAME = "offer_ids"
REDIS_LIST_OFFER_IDS_IN_ERROR_NAME = "offer_ids_in_error"
REDIS_LIST_VENUE_IDS_FOR_OFFERS_NAME = "venue_ids_for_offers"
REDIS_LIST_VENUE_IDS_NAME = "venue_ids_new"
REDIS_HASHMAP_INDEXED_OFFERS_NAME = "indexed_offers"

DEFAULT_LONGITUDE_FOR_NUMERIC_OFFER = 2.409289
DEFAULT_LATITUDE_FOR_NUMERIC_OFFER = 47.158459


class AlgoliaBackend(base.SearchBackend):
    def __init__(self):
        super().__init__()
        client = algoliasearch.search_client.SearchClient.create(
            app_id=settings.ALGOLIA_APPLICATION_ID, api_key=settings.ALGOLIA_API_KEY
        )
        self.algolia_client = client.init_index(settings.ALGOLIA_INDEX_NAME)
        self.redis_client = current_app.redis_client

    def enqueue_offer_ids(self, offer_ids: Iterable[int]) -> None:
        if not offer_ids:
            return
        try:
            self.redis_client.rpush(REDIS_LIST_OFFER_IDS_NAME, *offer_ids)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not add offers to indexation queue", extra={"offers": offer_ids})

    def enqueue_offer_ids_in_error(self, offer_ids: Iterable[int]) -> None:
        if not offer_ids:
            return
        try:
            self.redis_client.rpush(REDIS_LIST_OFFER_IDS_IN_ERROR_NAME, *offer_ids)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not add offers to error queue", extra={"offers": offer_ids})

    def enqueue_venue_ids_for_offers(self, venue_ids: Iterable[int]) -> None:
        if not venue_ids:
            return
        try:
            self.redis_client.rpush(REDIS_LIST_VENUE_IDS_FOR_OFFERS_NAME, *venue_ids)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not add venues to indexation queue", extra={"venues": venue_ids})

    def pop_offer_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        # Here we should use `LPOP` but its `count` argument has been
        # added in Redis 6.2. GCP currently has an earlier version of
        # Redis (5.0), where we can pop only one item at once. As a
        # work around, we get and delete items within a pipeline,
        # which should be atomic.
        #
        # The error handling is minimal:
        # - if the get fails, the function returns an empty list. It's
        #   fine, the next run may have more chance and may work;
        # - if the delete fails, we'll process the same batch
        #   twice. It's not optimal, but it's ok.
        if from_error_queue:
            redis_list_name = REDIS_LIST_OFFER_IDS_IN_ERROR_NAME
        else:
            redis_list_name = REDIS_LIST_OFFER_IDS_NAME

        offer_ids = set()
        try:
            pipeline = self.redis_client.pipeline(transaction=True)
            pipeline.lrange(redis_list_name, 0, count - 1)
            pipeline.ltrim(redis_list_name, count, -1)
            results = pipeline.execute()
            offer_ids = {int(offer_id) for offer_id in results[0]}  # str -> int
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not pop offer ids to index from queue")
        finally:
            pipeline.reset()
        return offer_ids

    def get_venue_ids_for_offers_from_queue(self, count: int) -> set[int]:
        try:
            venue_ids = self.redis_client.lrange(REDIS_LIST_VENUE_IDS_FOR_OFFERS_NAME, 0, count - 1)
            return {int(venue_id) for venue_id in venue_ids}  # str -> int
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not get venue ids to index from queue")
            return set()

    def delete_venue_ids_for_offers_from_queue(self, venue_ids: Iterable[int]) -> None:
        if not venue_ids:
            return
        try:
            for venue_id in venue_ids:
                # count=0 means "remove all occurrences of this value"
                self.redis_client.lrem(REDIS_LIST_VENUE_IDS_FOR_OFFERS_NAME, count=0, value=venue_id)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not delete indexed venue ids from queue")

    def count_offers_to_index_from_queue(self, from_error_queue: bool = False) -> int:
        if from_error_queue:
            redis_list_name = REDIS_LIST_OFFER_IDS_IN_ERROR_NAME
        else:
            redis_list_name = REDIS_LIST_OFFER_IDS_NAME
        try:
            return self.redis_client.llen(redis_list_name)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not count offers left to index from queue")
            return 0

    def check_offer_is_indexed(self, offer: offers_models.Offer) -> bool:
        try:
            return self.redis_client.hexists(REDIS_HASHMAP_INDEXED_OFFERS_NAME, offer.id)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not check whether offer exists in cache", extra={"offer": offer.id})
            # This function is only used to avoid an unnecessary
            # deletion request to Algolia if the offer is not in the
            # cache. Here we don't know, so we'll say it's in the
            # cache so that we do perform a request to Algolia.
            return True

    def index_offers(self, offers: Iterable[offers_models.Offer]) -> None:
        if not offers:
            return
        objects = [self.serialize_offer(offer) for offer in offers]
        self.algolia_client.save_objects(objects)
        try:
            # We used to store a summary of each offer, which is why
            # we used hashmap and not a set. But since we don't need
            # the value anymore, we can store the lightest object
            # possible to make Redis use less memory. In the future,
            # we may even remove the hashmap if it's not proven useful
            # (see log in reindex_offer_ids)
            offer_ids = [offer.id for offer in offers]
            pipeline = self.redis_client.pipeline(transaction=True)
            for offer_id in offer_ids:
                pipeline.hset(REDIS_HASHMAP_INDEXED_OFFERS_NAME, offer_id, "")
            pipeline.execute()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Could not add to list of indexed offers", extra={"offers": offer_ids})
        finally:
            pipeline.reset()

    def unindex_offer_ids(self, offer_ids: Iterable[int]) -> None:
        if not offer_ids:
            return
        self.algolia_client.delete_objects(offer_ids)
        try:
            self.redis_client.hdel(REDIS_HASHMAP_INDEXED_OFFERS_NAME, *offer_ids)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not remove offers from indexed offers set", extra={"offers": offer_ids})

    def unindex_all_offers(self) -> None:
        self.algolia_client.clear_objects()
        try:
            self.redis_client.delete(REDIS_HASHMAP_INDEXED_OFFERS_NAME)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not clear indexed offers cache",
            )

    @classmethod
    def serialize_offer(cls, offer: offers_models.Offer) -> dict:
        venue = offer.venue
        offerer = venue.managingOfferer
        humanize_offer_id = humanize(offer.id)
        has_coordinates = venue.latitude is not None and venue.longitude is not None
        author = offer.extraData and offer.extraData.get("author")
        stage_director = offer.extraData and offer.extraData.get("stageDirector")
        visa = offer.extraData and offer.extraData.get("visa")
        # FIXME (cgaunet, 2021-05-10): this is to prevent duplicates in Algolia.
        # When it's possible to remove duplicates on many attributes, remove the visa part from the isbn field.
        isbn = offer.extraData and (offer.extraData.get("isbn") or offer.extraData.get("visa"))
        speaker = offer.extraData and offer.extraData.get("speaker")
        performer = offer.extraData and offer.extraData.get("performer")
        show_type = offer.extraData and offer.extraData.get("showType")
        show_sub_type = offer.extraData and offer.extraData.get("showSubType")
        music_type = offer.extraData and offer.extraData.get("musicType")
        music_sub_type = offer.extraData and offer.extraData.get("musicSubType")
        prices = map(lambda stock: stock.price, offer.bookableStocks)
        prices_sorted = sorted(prices, key=float)
        price_min = prices_sorted[0]
        price_max = prices_sorted[-1]
        dates = []
        times = []
        if offer.isEvent:
            dates = [stock.beginningDatetime.timestamp() for stock in offer.bookableStocks]
            times = [
                date_utils.get_time_in_seconds_from_datetime(stock.beginningDatetime) for stock in offer.bookableStocks
            ]
        date_created = offer.dateCreated.timestamp()
        stocks_date_created = [stock.dateCreated.timestamp() for stock in offer.bookableStocks]
        tags = [criterion.name for criterion in offer.criteria]

        object_to_index = {
            "objectID": offer.id,
            "offer": {
                "subcategoryLabel": offer.subcategory.app_label,
                "author": author,
                "category": offer.offer_category_name_for_app,
                "rankingWeight": offer.rankingWeight,
                "dateCreated": date_created,
                "dates": sorted(dates),
                "description": offer.description,
                "id": humanize_offer_id,
                "pk": offer.id,
                "isbn": isbn,
                "isDigital": offer.isDigital,
                "isDuo": offer.isDuo,
                "isEducational": offer.isEducational,
                "isEvent": offer.isEvent,
                "isThing": offer.isThing,
                # FIXME remove once subcategory logic is fully implemented
                "label": offer.offerType["appLabel"],
                "musicSubType": music_sub_type,
                "musicType": music_type,
                "name": offer.name,
                "performer": performer,
                "prices": prices_sorted,
                "priceMin": price_min,
                "priceMax": price_max,
                "searchGroup": offer.subcategory.search_group,
                "showSubType": show_sub_type,
                "showType": show_type,
                "speaker": speaker,
                "stageDirector": stage_director,
                "stocksDateCreated": sorted(stocks_date_created),
                # PC-8526: Warning: we should not store the full url of the image but only the path.
                # Currrently we store `OBJECT_STORAGE_URL/path`, but we should store `path` and build the
                # full url in the frontend.
                "thumbUrl": offer.thumbUrl,
                "tags": tags,
                "times": list(set(times)),
                "type": offer.offerType["sublabel"],
                "visa": visa,
                "withdrawalDetails": offer.withdrawalDetails,
            },
            "offerer": {
                "name": offerer.name,
            },
            "venue": {
                "city": venue.city,
                "departementCode": venue.departementCode,
                "name": venue.name,
                "publicName": venue.publicName,
            },
        }

        if has_coordinates:
            object_to_index.update({"_geoloc": {"lat": float(venue.latitude), "lng": float(venue.longitude)}})
        else:
            object_to_index.update(
                {"_geoloc": {"lat": DEFAULT_LATITUDE_FOR_NUMERIC_OFFER, "lng": DEFAULT_LONGITUDE_FOR_NUMERIC_OFFER}}
            )

        return object_to_index
