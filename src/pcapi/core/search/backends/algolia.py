import logging
import re
from typing import Iterable
import urllib.parse

import algoliasearch.search_client
from flask import current_app
import redis

from pcapi import settings
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import base
import pcapi.utils.date as date_utils
from pcapi.utils.human_ids import humanize
from pcapi.utils.stopwords import STOPWORDS


logger = logging.getLogger(__name__)

# FIXME (dbaty, 2021-10-15): these are all lists, which are less
# usable for us than sets. See also `redis_lpop()` below, which we
# would not have to implement if we were using sets (because `SPOP`
# does allow to pop multiple items at once with our Redis version).
REDIS_LIST_OFFER_IDS_NAME = "offer_ids"
REDIS_LIST_OFFER_IDS_IN_ERROR_NAME = "offer_ids_in_error"
REDIS_LIST_VENUE_IDS_FOR_OFFERS_NAME = "venue_ids_for_offers"
REDIS_VENUE_IDS_TO_INDEX = "search:algolia:venue-ids-to-index"
REDIS_VENUE_IDS_IN_ERROR_TO_INDEX = "search:algolia:venue-ids-in-error-to-index"
REDIS_HASHMAP_INDEXED_OFFERS_NAME = "indexed_offers"

DEFAULT_LONGITUDE = 2.409289
DEFAULT_LATITUDE = 47.158459

WORD_SPLITTER = re.compile(r"\W+")


def url_path(url):
    """Return the path component of a URL.

    Example::

        >>> url_path("https://example.com/foo/bar/baz?a=1")
        "/foo/bar/baz?a=1"
    """
    if not url:
        return None
    parts = urllib.parse.urlparse(url)
    path = parts.path
    if parts.query:
        path += f"?{parts.query}"
    if parts.fragment:
        path += f"#{parts.fragment}"
    return path


def remove_stopwords(s: str) -> str:
    """Remove French stopwords from the given string and return what's
    left, lowercased.

    We are not interested in being thorough. Algolia takes care of
    ignoring stopwords and does it better than we do. Here we are
    mostly interested in storing less data in Algolia. But we want
    to keep the order in which words appear (because it matters in
    Algolia).
    """
    words = [word for word in WORD_SPLITTER.split(s.lower()) if word and word not in STOPWORDS]
    return " ".join(words)


class AlgoliaBackend(base.SearchBackend):
    def __init__(self):
        super().__init__()
        client = algoliasearch.search_client.SearchClient.create(
            app_id=settings.ALGOLIA_APPLICATION_ID, api_key=settings.ALGOLIA_API_KEY
        )
        self.algolia_offers_client = client.init_index(settings.ALGOLIA_OFFERS_INDEX_NAME)
        self.algolia_venues_client = client.init_index(settings.ALGOLIA_VENUES_INDEX_NAME)
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

    def enqueue_venue_ids(self, venue_ids: Iterable[int]) -> None:
        return self._enqueue_venue_ids(venue_ids, REDIS_VENUE_IDS_TO_INDEX)

    def enqueue_venue_ids_in_error(self, venue_ids: Iterable[int]) -> None:
        return self._enqueue_venue_ids(venue_ids, REDIS_VENUE_IDS_IN_ERROR_TO_INDEX)

    def enqueue_venue_ids_for_offers(self, venue_ids: Iterable[int]) -> None:
        return self._enqueue_venue_ids_legacy_for_list(venue_ids, REDIS_LIST_VENUE_IDS_FOR_OFFERS_NAME)

    def _enqueue_venue_ids(self, venue_ids: Iterable[int], queue_name: str) -> None:
        if not venue_ids:
            return
        try:
            self.redis_client.sadd(queue_name, *venue_ids)
        except redis.exceptions.RedisError:
            logger.exception(
                "Could not add venues to indexation queue", extra={"venues": venue_ids, "queue": queue_name}
            )

    def _enqueue_venue_ids_legacy_for_list(self, venue_ids: Iterable[int], queue_name: str) -> None:
        if not venue_ids:
            return
        try:
            self.redis_client.rpush(queue_name, *venue_ids)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not add venues to indexation queue", extra={"venues": venue_ids, "queue": queue_name}
            )

    def pop_offer_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        if from_error_queue:
            redis_list_name = REDIS_LIST_OFFER_IDS_IN_ERROR_NAME
        else:
            redis_list_name = REDIS_LIST_OFFER_IDS_NAME

        return self.redis_lpop(redis_list_name, count)

    def pop_venue_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        if from_error_queue:
            redis_set_name = REDIS_VENUE_IDS_IN_ERROR_TO_INDEX
        else:
            redis_set_name = REDIS_VENUE_IDS_TO_INDEX
        try:
            offer_ids = self.redis_client.spop(redis_set_name, count)
            return {int(offer_id) for offer_id in offer_ids}  # str -> int
        except redis.exceptions.RedisError:
            logger.exception("Could not pop offer ids to index from queue", extra={"queue": redis_set_name})
            return set()

    def pop_venue_ids_for_offers_from_queue(self, count: int) -> set[int]:
        return self.redis_lpop(REDIS_LIST_VENUE_IDS_FOR_OFFERS_NAME, count)

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
        self.algolia_offers_client.save_objects(objects)
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

    def index_venues(self, venues: Iterable[offerers_models.Venue]) -> None:
        if not venues:
            return
        objects = [self.serialize_venue(venue) for venue in venues]
        self.algolia_venues_client.save_objects(objects)

    def unindex_offer_ids(self, offer_ids: Iterable[int]) -> None:
        if not offer_ids:
            return
        self.algolia_offers_client.delete_objects(offer_ids)
        try:
            self.redis_client.hdel(REDIS_HASHMAP_INDEXED_OFFERS_NAME, *offer_ids)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not remove offers from indexed offers set", extra={"offers": offer_ids})

    def unindex_all_offers(self) -> None:
        self.algolia_offers_client.clear_objects()
        try:
            self.redis_client.delete(REDIS_HASHMAP_INDEXED_OFFERS_NAME)
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not clear indexed offers cache",
            )

    def unindex_venue_ids(self, venue_ids: Iterable[int]) -> None:
        if not venue_ids:
            return
        self.algolia_venues_client.delete_objects(venue_ids)

    def unindex_all_venues(self) -> None:
        self.algolia_venues_client.clear_objects()

    @classmethod
    def serialize_offer(cls, offer: offers_models.Offer) -> dict:
        venue = offer.venue
        offerer = venue.managingOfferer
        humanize_offer_id = humanize(offer.id)
        extra_data = offer.extraData or {}
        visa = extra_data.get("visa")
        # FIXME (cgaunet, 2021-05-10): this is to prevent duplicates in Algolia.
        # When it's possible to remove duplicates on many attributes, remove the visa part from the isbn field.
        isbn = extra_data.get("isbn") or visa
        prices = map(lambda stock: stock.price, offer.bookableStocks)
        prices_sorted = sorted(prices, key=float)
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
        artist = " ".join(extra_data.get(key, "") for key in ("author", "performer", "speaker", "stageDirector"))

        object_to_index = {
            "objectID": offer.id,
            "offer": {
                "artist": artist.strip() or None,
                "category": offer.offer_category_name_for_app,
                "rankingWeight": offer.rankingWeight,
                "dateCreated": date_created,
                "dates": sorted(dates),
                "description": remove_stopwords(offer.description or ""),
                # TODO(antoinewg): still used for webapp: delete when migration to decliweb complete
                "id": humanize_offer_id,
                # TODO(antoinewg): regroup under group
                "isbn": isbn,
                "isDigital": offer.isDigital,
                "isDuo": offer.isDuo,
                "isEducational": offer.isEducational,
                "isEvent": offer.isEvent,
                "isThing": offer.isThing,
                # FIXME remove once subcategory logic is fully implemented
                "label": offer.subcategory.app_label,
                "name": offer.name,
                "prices": prices_sorted,
                "searchGroupName": offer.subcategory.search_group_name,
                "stocksDateCreated": sorted(stocks_date_created),
                "subcategoryId": offer.subcategory.id,
                "thumbUrl": url_path(offer.thumbUrl),
                "tags": tags,
                "times": list(set(times)),
                # TODO(antoinewg): regroup under group
                "visa": visa,
            },
            "offerer": {
                "name": offerer.name,
            },
            "venue": {
                "departementCode": venue.departementCode,
                "id": venue.id,
                "name": venue.name,
                "publicName": venue.publicName,
            },
            "_geoloc": position(venue),
        }

        return object_to_index

    @classmethod
    def serialize_venue(cls, venue: offerers_models.Venue) -> dict:
        social_medias = getattr(venue.contact, "social_medias", {})
        return {
            "objectID": venue.id,
            "name": venue.publicName or venue.name,
            "offerer_name": venue.managingOfferer.name,
            "venue_type": venue.venueTypeCode.name,
            "description": venue.description,
            "audio_disability": venue.audioDisabilityCompliant,
            "mental_disability": venue.mentalDisabilityCompliant,
            "motor_disability": venue.motorDisabilityCompliant,
            "visual_disability": venue.visualDisabilityCompliant,
            "email": getattr(venue.contact, "email", None),
            "phone_number": getattr(venue.contact, "phone_number", None),
            "website": getattr(venue.contact, "website", None),
            "facebook": social_medias.get("facebook"),
            "twitter": social_medias.get("twitter"),
            "instagram": social_medias.get("instagram"),
            "snapchat": social_medias.get("snapchat"),
            "_geoloc": position(venue),
        }

    def redis_lpop(self, queue_name: str, count: int) -> set[int]:
        """
        Here we can't use `LPOP` because its `count` argument has been
        added in Redis 6.2. GCP currently has an earlier version of
        Redis (5.0), where we can pop only one item at once. As a
        work around, we get and delete items within a pipeline,
        which should be atomic.

        The error handling is minimal:
        - if the get fails, the function returns an empty list. It's
          fine, the next run may have more chance and may work;
        - if the delete fails, we'll process the same batch
          twice. It's not optimal, but it's ok.
        """
        obj_ids = set()

        try:
            pipeline = self.redis_client.pipeline(transaction=True)

            pipeline.lrange(queue_name, 0, count - 1)
            pipeline.ltrim(queue_name, count, -1)

            results = pipeline.execute()
            obj_ids = {int(obj_id) for obj_id in results[0]}
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not pop obj ids to index from queue")
        finally:
            pipeline.reset()

        return obj_ids


def position(venue):
    latitude = venue.latitude or DEFAULT_LATITUDE
    longitude = venue.longitude or DEFAULT_LONGITUDE
    return {"lat": float(latitude), "lng": float(longitude)}
