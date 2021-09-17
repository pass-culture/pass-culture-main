import datetime
import decimal
import enum
import json
import logging
import typing
from typing import Iterable
import urllib.parse

from flask import current_app
import redis

from pcapi import settings
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.utils import requests
import pcapi.utils.date as date_utils

from . import base


REDIS_OFFER_IDS_TO_INDEX = "search:appsearch:offer-ids-to-index"
REDIS_OFFER_IDS_IN_ERROR_TO_INDEX = "search:appsearch:offer-ids-in-error-to-index"
REDIS_VENUE_IDS_FOR_OFFERS_TO_INDEX = "search:appsearch:venue-ids-for-offers-to-index"
REDIS_VENUE_IDS_TO_INDEX = "search:appsearch:venue-ids-new-to-index"

ENGINE_LANGUAGE = "fr"
# The App Search API accepts up to 100 documents per request
# (https://www.elastic.co/guide/en/app-search/current/documents.html#documents-create).
DOCUMENTS_PER_REQUEST_LIMIT = 100


OFFERS_ENGINE_NAME = "offers"

OFFERS_SCHEMA = {
    "subcategory_label": "text",
    "artist": "text",
    "category": "text",
    "date_created": "date",
    "dates": "date",
    "description": "text",
    "group": "text",
    "is_digital": "number",
    "is_duo": "number",
    "is_educational": "number",
    "is_event": "number",
    "is_thing": "number",
    # FIXME remove once subcategory logic is fully implemented
    "label": "text",
    "name": "text",
    # "id": "number",  must not be provided when creating the schema.
    "prices": "number",
    "ranking_weight": "number",
    "search_group": "text",
    "stocks_date_created": "date",
    "tags": "text",
    "times": "number",
    "thumb_url": "text",
    "offerer_name": "text",
    "venue_id": "number",
    "venue_department_code": "text",
    "venue_name": "text",
    "venue_position": "geolocation",
    "venue_public_name": "text",
}

OFFERS_SYNONYM_SET = (
    {"anime digital network", "ADN"},
    {"deezer", "spotify"},
    {"shingeki no kyojin", "snk", "l'attaque des titans"},
    {"OSC", "OCS", "netflix"},
    {"micro", "musique"},
    {"audible", "j'écoute malin j'écoute audible"},
    {"canal", "canal+", "canal +", "canal plus", "netflix"},
    {"tome", "T."},
)

VENUES_ENGINE_NAME = "venues"

VENUES_SCHEMA = {
    "name": "text",
    "offerer_name": "text",
    "venue_type": "text",
    "position": "geolocation",
    "description": "text",
    "audio_disability": "number",
    "mental_disability": "number",
    "motor_disability": "number",
    "visual_disability": "number",
    "email": "text",
    "phone_number": "text",
    "website": "text",
    "facebook": "text",
    "twitter": "text",
    "instagram": "text",
    "snapchat": "text",
}

VENUES_SYNONYM_SET = ()


logger = logging.getLogger(__name__)


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


def to_app_search_bool(value: typing.Optional[int]):
    """Return 0, 1 or ``None`` for boolean values.

    App Search does not have a boolean type. We index boolean values
    as integers instead.
    """
    if value is None:
        return None
    return int(value)


def get_batches(iterable, size=1):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


class AppSearchBackend(base.SearchBackend):
    def __init__(self):
        super().__init__()
        self.offers_engine = AppSearchApiClient(
            host=settings.APPSEARCH_HOST,
            api_key=settings.APPSEARCH_API_KEY,
            engine_name=OFFERS_ENGINE_NAME,
            synonyms=OFFERS_SYNONYM_SET,
            schema=OFFERS_SCHEMA,
        )

        self.venues_engine = AppSearchApiClient(
            host=settings.APPSEARCH_HOST,
            api_key=settings.APPSEARCH_API_KEY,
            engine_name=VENUES_ENGINE_NAME,
            synonyms=VENUES_SYNONYM_SET,
            schema=VENUES_SCHEMA,
        )

        self.redis_client = current_app.redis_client

    def enqueue_offer_ids(self, offer_ids: Iterable[int]):
        if not offer_ids:
            return
        try:
            self.redis_client.sadd(REDIS_OFFER_IDS_TO_INDEX, *offer_ids)
        except redis.exceptions.RedisError:
            logger.exception("Could not add offers to indexation queue", extra={"offers": offer_ids})

    def enqueue_offer_ids_in_error(self, offer_ids: Iterable[int]):
        if not offer_ids:
            return
        try:
            self.redis_client.sadd(REDIS_OFFER_IDS_IN_ERROR_TO_INDEX, *offer_ids)
        except redis.exceptions.RedisError:
            logger.exception("Could not add offers to error queue", extra={"offers": offer_ids})

    def enqueue_venue_ids(self, venue_ids: Iterable[int]):
        return self._enqueue_venue_ids(venue_ids, REDIS_VENUE_IDS_TO_INDEX)

    def enqueue_venue_ids_for_offers(self, venue_ids: Iterable[int]):
        return self._enqueue_venue_ids(venue_ids, REDIS_VENUE_IDS_FOR_OFFERS_TO_INDEX)

    def _enqueue_venue_ids(self, venue_ids: Iterable[int], queue_name: str) -> None:
        if not venue_ids:
            return
        try:
            self.redis_client.sadd(queue_name, *venue_ids)
        except redis.exceptions.RedisError:
            logger.exception(
                "Could not add venues to indexation queue", extra={"venues": venue_ids, "queue": queue_name}
            )

    def pop_offer_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        if from_error_queue:
            redis_set_name = REDIS_OFFER_IDS_IN_ERROR_TO_INDEX
        else:
            redis_set_name = REDIS_OFFER_IDS_TO_INDEX

        try:
            offer_ids = self.redis_client.spop(redis_set_name, count)
            return {int(offer_id) for offer_id in offer_ids}  # str -> int
        except redis.exceptions.RedisError:
            logger.exception("Could not pop offer ids to index from queue")
            return set()

    def get_venue_ids_from_queue(self, count: int) -> set[int]:
        return self._get_venue_ids_from_queue(count, REDIS_VENUE_IDS_TO_INDEX)

    def get_venue_ids_for_offers_from_queue(self, count: int) -> set[int]:
        return self._get_venue_ids_from_queue(count, REDIS_VENUE_IDS_FOR_OFFERS_TO_INDEX)

    def _get_venue_ids_from_queue(self, count: int, queue_name: str) -> set[int]:
        try:
            venue_ids = self.redis_client.srandmember(queue_name, count)
            return {int(venue_id) for venue_id in venue_ids}  # str -> int
        except redis.exceptions.RedisError:
            logger.exception("Could not get venue ids for offers to index from queue", extra={"queue": queue_name})
            return set()

    def delete_venue_ids_from_queue(self, venue_ids: Iterable[int]) -> None:
        return self._delete_venue_ids_from_queue(venue_ids, REDIS_VENUE_IDS_TO_INDEX)

    def delete_venue_ids_for_offers_from_queue(self, venue_ids: Iterable[int]) -> None:
        return self._delete_venue_ids_from_queue(venue_ids, REDIS_VENUE_IDS_FOR_OFFERS_TO_INDEX)

    def _delete_venue_ids_from_queue(self, venue_ids: Iterable[int], queue_name: str) -> None:
        if not venue_ids:
            return
        try:
            self.redis_client.srem(queue_name, *venue_ids)
        except redis.exceptions.RedisError:
            logger.exception("Could not delete indexed venue ids from queue", extra={"queue": queue_name})

    def count_offers_to_index_from_queue(self, from_error_queue: bool = False) -> int:
        if from_error_queue:
            redis_set_name = REDIS_OFFER_IDS_IN_ERROR_TO_INDEX
        else:
            redis_set_name = REDIS_OFFER_IDS_TO_INDEX

        try:
            return self.redis_client.scard(redis_set_name)
        except redis.exceptions.RedisError:
            logger.exception("Could not count offers left to index from queue")
            return 0

    def check_offer_is_indexed(self, offer: offers_models.Offer) -> bool:
        # FIXME (dbaty, 2021-07-15): this is a no-op on App Search.
        # Once we have removed the Algolia backend, we can remove this
        # method. It is only used to avoid an unnecessary deletion
        # request to App Search if the offer is not already indexed.
        # But it should rarely happen. And having to store a very
        # large number of ids in a set in Redis does not look like a
        # good idea.
        return True

    def index_offers(self, offers: Iterable[offers_models.Offer]) -> None:
        if not offers:
            return
        documents = [self.serialize_offer(offer) for offer in offers]
        self.offers_engine.create_or_update_documents(documents)

    def index_venues(self, venues: Iterable[offerers_models.Venue]) -> None:
        if not venues:
            return
        documents = [self.serialize_venue(venue) for venue in venues]
        self.venues_engine.create_or_update_documents(documents)

    def unindex_offer_ids(self, offer_ids: Iterable[int]) -> None:
        if not offer_ids:
            return
        self.offers_engine.delete_documents(offer_ids)

    def unindex_all_offers(self) -> None:
        self.offers_engine.delete_all_documents()

    def unindex_venue_ids(self, venue_ids: Iterable[int]) -> None:
        if not venue_ids:
            return
        self.venues_engine.delete_documents(venue_ids)

    def unindex_all_venues(self) -> None:
        self.venues_engine.delete_all_documents()

    @classmethod
    def serialize_offer(cls, offer: offers_models.Offer) -> dict:
        stocks = offer.bookableStocks
        dates = []
        times = []
        if offer.isEvent:
            dates = [stock.beginningDatetime for stock in stocks]
            times = [date_utils.get_time_in_seconds_from_datetime(stock.beginningDatetime) for stock in stocks]

        extra_data = offer.extraData or {}
        # This field is used to show a single search result when
        # multiple offers of the same product are returned (for
        # example, the same book or the same movie in multiple
        # locations).
        group = (extra_data.get("isbn") or extra_data.get("visa")) if extra_data else None
        if not group:
            group = str(offer.id)

        artist = " ".join(extra_data.get(key, "") for key in ("author", "performer", "speaker", "stageDirector"))

        venue = offer.venue
        return {
            "subcategory_label": offer.subcategory.app_label,
            "artist": artist.strip() or None,
            "category": offer.offer_category_name_for_app,
            "date_created": offer.dateCreated,  # used only to rank results
            "dates": dates,
            "description": offer.description,
            "group": group,
            "is_digital": to_app_search_bool(offer.isDigital),
            "is_duo": to_app_search_bool(offer.isDuo),
            "is_educational": to_app_search_bool(offer.isEducational),
            "is_event": to_app_search_bool(offer.isEvent),
            "is_thing": to_app_search_bool(offer.isThing),
            "label": offer.offerType["appLabel"],
            "name": offer.name,
            "id": offer.id,
            "prices": [int(stock.price * 100) for stock in stocks],
            "ranking_weight": offer.rankingWeight or 0,
            "search_group": offer.subcategory.search_group,
            "stocks_date_created": [stock.dateCreated for stock in stocks],
            "tags": [criterion.name for criterion in offer.criteria],
            "times": times,
            "thumb_url": url_path(offer.thumbUrl),
            "offerer_name": venue.managingOfferer.name,
            "venue_department_code": venue.departementCode,
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_position": position(venue),
            "venue_public_name": venue.publicName,
        }

    @classmethod
    def serialize_venue(cls, venue: offerers_models.Venue) -> dict:
        social_medias = getattr(venue.contact, "social_medias", {})
        return {
            "id": venue.id,
            "name": venue.publicName or venue.name,
            "offerer_name": venue.managingOfferer.name,
            "venue_type": venue.venueTypeCode.name,
            "position": position(venue),
            "description": venue.description,
            "audio_disability": to_app_search_bool(venue.audioDisabilityCompliant),
            "mental_disability": to_app_search_bool(venue.mentalDisabilityCompliant),
            "motor_disability": to_app_search_bool(venue.motorDisabilityCompliant),
            "visual_disability": to_app_search_bool(venue.visualDisabilityCompliant),
            "email": getattr(venue.contact, "email", None),
            "phone_number": getattr(venue.contact, "phone_number", None),
            "website": getattr(venue.contact, "website", None),
            "facebook": social_medias.get("facebook"),
            "twitter": social_medias.get("twitter"),
            "instagram": social_medias.get("instagram"),
            "snapchat": social_medias.get("snapchat"),
        }


class AppSearchApiClient:
    def __init__(self, host: str, api_key: str, engine_name: str, synonyms: Iterable[set[str]], schema: dict[str, str]):
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.engine_name = engine_name
        self.synonyms = synonyms
        self.schema = schema

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    # Engines API: https://www.elastic.co/guide/en/app-search/current/engines.html
    @property
    def engines_url(self):
        path = "/api/as/v1/engines"
        return f"{self.host}{path}"

    def create_engine(self):
        data = {"name": self.engine_name, "language": ENGINE_LANGUAGE}
        response = requests.post(self.engines_url, headers=self.headers, json=data)
        return response

    # Schema API: https://www.elastic.co/guide/en/app-search/current/schema.html
    @property
    def schema_url(self):
        path = f"/api/as/v1/engines/{self.engine_name}/schema"
        return f"{self.host}{path}"

    def update_schema(self):
        response = requests.post(self.schema_url, headers=self.headers, json=self.schema)
        return response

    # Synonyms API: https://www.elastic.co/guide/en/app-search/current/synonyms.html
    @property
    def synonyms_url(self):
        path = f"/api/as/v1/engines/{self.engine_name}/synonyms"
        return f"{self.host}{path}"

    def update_synonyms(self):
        for synonym_set in self.synonyms:
            data = {"synonyms": list(synonym_set)}
            response = requests.post(self.synonyms_url, headers=self.headers, json=data)
            yield response

    # Documents API: https://www.elastic.co/guide/en/app-search/current/documents.html
    @property
    def documents_url(self):
        path = f"/api/as/v1/engines/{self.engine_name}/documents"
        return f"{self.host}{path}"

    def create_or_update_documents(self, documents: Iterable[dict]):
        # Error handling is done by the caller.
        for batch in get_batches(documents, size=DOCUMENTS_PER_REQUEST_LIMIT):
            data = json.dumps(batch, cls=AppSearchJsonEncoder)
            response = requests.post(self.documents_url, headers=self.headers, data=data)
            response.raise_for_status()
            # Except here when App Search returns a 200 OK response
            # even if *some* documents cannot be processed. In that
            # case we log it here. It denotes a bug on our side: type
            # mismatch on a field, bogus JSON serialization, etc.
            response_data = response.json()
            errors = [item for item in response_data if item["errors"]]
            if errors:
                logger.error("Some documents could not be indexed, possible typing bug", extra={"errors": errors})

    def delete_documents(self, document_ids: Iterable[int]):
        # Error handling is done by the caller.
        for batch in get_batches(document_ids, size=DOCUMENTS_PER_REQUEST_LIMIT):
            data = json.dumps(batch)
            response = requests.delete(self.documents_url, headers=self.headers, data=data)
            response.raise_for_status()

    def delete_all_documents(self):
        if settings.IS_PROD:
            raise ValueError("You cannot delete all documents on production.")
        # As of 2021-07-16, there is no endpoint to delete all
        # documents. We need to fetch all documents.
        # Error handling is done by the caller.
        list_url = f"{self.documents_url}/list"
        page = 1
        while True:
            page_data = {"page": {"page": page, "size": DOCUMENTS_PER_REQUEST_LIMIT}}
            response = requests.get(list_url, headers=self.headers, json=page_data)
            document_ids = [document["id"] for document in response.json()["results"]]
            if not document_ids:
                break
            self.delete_documents(document_ids)
            page += 1


class AppSearchJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat().split(".")[0] + "Z"
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, enum.Enum):
            return obj.name
        return super().default(obj)


def position(venue: offerers_models.Venue) -> typing.Optional[str]:
    if venue.longitude is not None and venue.latitude is not None:
        # It's important to send the position as text, not as an
        # array of floats. That way, App Search includes the field
        # in search results (even though the documentation says
        # that `geolocation` fields are not included).
        return f"{venue.latitude},{venue.longitude}"
    return None
