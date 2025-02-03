from collections import abc
import contextlib
import datetime
import decimal
import enum
import logging
import re
import typing
import urllib.parse

import algoliasearch.http.requester
import algoliasearch.search_client
from flask import current_app
import redis
import sqlalchemy as sa

from pcapi import settings
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.core.educational.academies import get_academy_from_department
import pcapi.core.educational.api.offer as educational_api_offer
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.utils import get_offer_address
from pcapi.core.providers import titelive_gtl
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.core.search import SearchError
from pcapi.core.search.backends import base
from pcapi.domain.music_types import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import SHOW_TYPES_LABEL_BY_CODE
from pcapi.models.feature import FeatureToggle
from pcapi.utils import human_ids
from pcapi.utils import requests
import pcapi.utils.date as date_utils
from pcapi.utils.regions import get_department_code_from_city_code
from pcapi.utils.stopwords import STOPWORDS


logger = logging.getLogger(__name__)

Numeric = float | decimal.Decimal
MAX_SEARCH_QUERY_COUNT = 1000

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


DEFAULT_LONGITUDE = 2.409289
DEFAULT_LATITUDE = 47.158459

WORD_SPLITTER = re.compile(r"\W+")


class Last30DaysBookingsRange(enum.Enum):
    VERY_LOW = "very-low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very-high"


def get_last_30_days_bookings_range(quantity: int) -> str | None:
    assert len(settings.ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS) == 4, (
        "bad value for setting ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS, "
        "it should contain 4 integers separated by commas."
    )
    low, medium, high, very_high = settings.ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS

    if quantity >= very_high:
        return Last30DaysBookingsRange.VERY_HIGH.value

    if quantity >= high:
        return Last30DaysBookingsRange.HIGH.value

    if quantity >= medium:
        return Last30DaysBookingsRange.MEDIUM.value

    if quantity >= low:
        return Last30DaysBookingsRange.LOW.value

    return Last30DaysBookingsRange.VERY_LOW.value


def url_path(url: str) -> str | None:
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


def create_algolia_client() -> algoliasearch.search_client.SearchClient:
    config = algoliasearch.search_client.SearchConfig(
        app_id=settings.ALGOLIA_APPLICATION_ID,
        api_key=settings.ALGOLIA_API_KEY,
    )
    requester = algoliasearch.http.requester.Requester()
    requester._session = requests.Session()  # inject our own session handler that logs
    transporter = algoliasearch.search_client.Transporter(requester, config)
    return algoliasearch.search_client.SearchClient(transporter, config)


class AlgoliaBackend(base.SearchBackend):
    def __init__(self) -> None:
        super().__init__()
        client = create_algolia_client()
        self.algolia_offers_client = client.init_index(settings.ALGOLIA_OFFERS_INDEX_NAME)
        self.algolia_collective_offers_templates_client = client.init_index(
            settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME
        )
        self.algolia_venues_client = client.init_index(settings.ALGOLIA_VENUES_INDEX_NAME)
        self.redis_client = current_app.redis_client

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

    def check_offer_is_indexed(self, offer: offers_models.Offer) -> bool:
        try:
            return self.redis_client.hexists(
                REDIS_HASHMAP_INDEXED_OFFERS_NAME,
                str(offer.id),
            )
        except redis.exceptions.RedisError:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not check whether offer exists in cache", extra={"offer": offer.id})
            # This function is only used to avoid an unnecessary
            # deletion request to Algolia if the offer is not in the
            # cache. Here we don't know, so we'll say it's in the
            # cache so that we do perform a request to Algolia.
            return True

    def index_offers(self, offers: abc.Collection[offers_models.Offer], last_30_days_bookings: dict[int, int]) -> None:
        if not offers:
            return
        objects = [self.serialize_offer(offer, last_30_days_bookings.get(offer.id) or 0) for offer in offers]
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
                pipeline.hset(REDIS_HASHMAP_INDEXED_OFFERS_NAME, str(offer_id), "")
            pipeline.execute()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Could not add to list of indexed offers", extra={"offers": offer_ids})
        finally:
            pipeline.reset()

    def index_collective_offer_templates(
        self,
        collective_offer_templates: abc.Collection[educational_models.CollectiveOfferTemplate],
    ) -> None:
        if not collective_offer_templates:
            return
        objects = [
            self.serialize_collective_offer_template(collective_offer_template)
            for collective_offer_template in collective_offer_templates
        ]
        self.algolia_collective_offers_templates_client.save_objects(objects)

    def index_venues(self, venues: abc.Collection[offerers_models.Venue]) -> None:
        if not venues:
            return
        objects = [self.serialize_venue(venue) for venue in venues]
        self.algolia_venues_client.save_objects(objects)

    def unindex_offer_ids(self, offer_ids: abc.Collection[int]) -> None:
        if not offer_ids:
            return
        self.algolia_offers_client.delete_objects(offer_ids)
        try:
            self.redis_client.hdel(
                REDIS_HASHMAP_INDEXED_OFFERS_NAME,
                *(str(offer_id) for offer_id in offer_ids),
            )
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

    def unindex_venue_ids(self, venue_ids: abc.Collection[int]) -> None:
        if not venue_ids:
            return
        self.algolia_venues_client.delete_objects(venue_ids)

    def unindex_collective_offer_template_ids(self, collective_offer_template_ids: abc.Collection[int]) -> None:
        if not collective_offer_template_ids:
            return
        self.algolia_collective_offers_templates_client.delete_objects(
            [
                _transform_collective_offer_template_id(collective_offer_template_id)
                for collective_offer_template_id in collective_offer_template_ids
            ]
        )

    def unindex_all_venues(self) -> None:
        self.algolia_venues_client.clear_objects()

    def unindex_all_collective_offer_templates(self) -> None:
        self.algolia_collective_offers_templates_client.clear_objects()

    @classmethod
    def serialize_offer(cls, offer: offers_models.Offer, last_30_days_bookings: int) -> dict:
        venue = offer.venue
        offerer = venue.managingOfferer
        prices = {stock.price for stock in offer.bookableStocks}
        dates = set()
        times = set()
        if offer.isEvent:
            dates = {stock.beginningDatetime.timestamp() for stock in offer.bookableStocks}  # type: ignore[union-attr]
            times = {
                date_utils.get_time_in_seconds_from_datetime(stock.beginningDatetime) for stock in offer.bookableStocks  # type: ignore[arg-type]
            }
        date_created = offer.dateCreated.timestamp()
        tags = [criterion.name for criterion in offer.criteria]

        extra_data = offer.product.extraData if offer.product and offer.product.extraData else offer.extraData or {}
        extra_data_artist = " ".join(
            str(extra_data.get(key, "")) for key in ("author", "performer", "speaker", "stageDirector")
        )
        artists = (
            [{"id": artist.id, "image": artist.image, "name": artist.name} for artist in offer.product.artists]
            if offer.product and offer.product.artists
            else None
        )
        release_date = None
        if extra_data.get("releaseDate"):
            try:
                release_date = datetime.datetime.fromisoformat(extra_data.get("releaseDate") or "").timestamp()
            except ValueError as exc:
                logger.error("Release date could not be parsed %s", exc)

        # Field used by Algolia (not the frontend) to deduplicate results
        # https://www.algolia.com/doc/api-reference/api-parameters/distinct/
        distinct = (
            str(extra_data.get("allocineId", "")) or extra_data.get("visa") or extra_data.get("ean") or str(offer.id)
        )
        gtl_id = extra_data.get("gtl_id")

        music_type_labels = []
        music_type = (extra_data.get("musicType") or "").strip()
        if music_type:
            if gtl_id and gtl_id in TITELIVE_MUSIC_GENRES_BY_GTL_ID:
                music_type_labels.append(TITELIVE_MUSIC_GENRES_BY_GTL_ID[gtl_id])

            try:
                music_type_labels.append(MUSIC_TYPES_LABEL_BY_CODE[int(music_type)])
            except (ValueError, KeyError, TypeError):
                logger.warning("bad music type encountered", extra={"offer": offer.id, "music_type": music_type})

        show_type_label = None
        show_type = (extra_data.get("showType") or "").strip()
        if show_type:
            try:
                show_type_label = SHOW_TYPES_LABEL_BY_CODE[int(show_type)]
            except (ValueError, KeyError, TypeError):
                logger.warning("bad show type encountered", extra={"offer": offer.id, "show_type": show_type})

        macro_section = None
        section = (extra_data.get("rayon") or "").strip().lower()
        if section:
            try:
                macro_section = (
                    offers_models.BookMacroSection.query.filter(
                        sa.func.lower(offers_models.BookMacroSection.section) == section
                    )
                    .with_entities(offers_models.BookMacroSection.macroSection)
                    .scalar()
                ).strip()
            except AttributeError:
                macro_section = None

        gtl = titelive_gtl.get_gtl(gtl_id) if gtl_id else None

        gtl_code_1 = gtl_code_2 = gtl_code_3 = gtl_code_4 = None
        if gtl_id:
            gtl_code_1 = gtl_id[:2] + "00" * 3
            gtl_code_2 = gtl_id[:4] + "00" * 2
            gtl_code_3 = gtl_id[:6] + "00" * 1
            gtl_code_4 = gtl_id

        offer_address = get_offer_address(offer)
        address = offer_address.street
        city = offer_address.city
        department_code = offer_address.departmentCode
        postal_code = offer_address.postalCode

        search_groups = (
            offer.subcategory.native_category.parents
            if offer.subcategory.native_category != subcategories_v2.NATIVE_CATEGORY_NONE
            else [offer.subcategory.search_group_name]
        )

        headline_offer = next(
            (headline_offer for headline_offer in offer.headlineOffers if headline_offer.isActive), None
        )

        # If you update this dictionary, please check whether you need to
        # also update `core.offerers.api.VENUE_ALGOLIA_INDEXED_FIELDS`.
        object_to_index: dict[str, typing.Any] = {
            "distinct": distinct,
            "objectID": offer.id,
            "offer": {
                "allocineId": extra_data.get("allocineId"),
                "artist": extra_data_artist.strip() or None,
                "bookMacroSection": macro_section,
                "dateCreated": date_created,
                "dates": sorted(dates),
                "description": remove_stopwords(offer.description or ""),
                "ean": extra_data.get("ean"),
                "gtlCodeLevel1": gtl_code_1,
                "gtlCodeLevel2": gtl_code_2,
                "gtlCodeLevel3": gtl_code_3,
                "gtlCodeLevel4": gtl_code_4,
                "indexedAt": datetime.datetime.utcnow().isoformat(),
                "isDigital": offer.isDigital,
                "isDuo": offer.isDuo,
                "isEducational": False,
                "isEvent": offer.isEvent,
                "isForbiddenToUnderage": offer.is_forbidden_to_underage,
                "isPermanent": offer.isPermanent,
                "isThing": offer.isThing,
                "last30DaysBookings": last_30_days_bookings,
                "last30DaysBookingsRange": get_last_30_days_bookings_range(last_30_days_bookings),
                "movieGenres": extra_data.get("genres"),
                "musicType": music_type_labels,
                "name": offer.name,
                "nativeCategoryId": offer.subcategory.native_category_id,
                "prices": sorted(prices),
                "rankingWeight": offer.rankingWeight,
                "releaseDate": release_date,
                "bookFormat": extra_data.get("bookFormat"),
                # TODO(thconte, 2024-08-23): keep searchGroups and remove
                # remove searchGroupNamev2 once app minimal version has been bumped
                "searchGroupNamev2": search_groups,
                "searchGroups": search_groups,
                "showType": show_type_label,
                "students": extra_data.get("students") or [],
                "subcategoryId": offer.subcategory.id,
                "tags": tags,
                "thumbUrl": url_path(offer.thumbUrl) if offer.thumbUrl else None,
                "times": list(times),
                "visa": extra_data.get("visa"),
            },
            "offerer": {
                "name": offerer.name,
            },
            "venue": {
                "address": address,
                "banner_url": venue.bannerUrl,
                "city": city,
                "departmentCode": department_code,
                "id": venue.id,
                "isAudioDisabilityCompliant": venue.audioDisabilityCompliant,
                "isMentalDisabilityCompliant": venue.mentalDisabilityCompliant,
                "isMotorDisabilityCompliant": venue.motorDisabilityCompliant,
                "isPermanent": venue.isPermanent,
                "isVisualDisabilityCompliant": venue.visualDisabilityCompliant,
                "name": venue.name,
                "postalCode": postal_code,
                "publicName": venue.publicName,
                "venue_type": venue.venueTypeCode.name,
            },
            "_geoloc": position(venue, offer),
        }

        if offer.subcategory.category.id == categories.LIVRE.id and gtl:
            object_to_index["offer"]["gtl_level1"] = gtl.get("level_01_label")
            object_to_index["offer"]["gtl_level2"] = gtl.get("level_02_label")
            object_to_index["offer"]["gtl_level3"] = gtl.get("level_03_label")
            object_to_index["offer"]["gtl_level4"] = gtl.get("level_04_label")
        elif gtl_id and offer.subcategory.category.id in (
            categories.MUSIQUE_ENREGISTREE.id,
            categories.MUSIQUE_LIVE.id,
        ):
            gtl_label = next(
                (music_type.label for music_type in categories.TITELIVE_MUSIC_TYPES if music_type.gtl_id == gtl_id),
                None,
            )
            object_to_index["offer"]["gtl_level1"] = gtl_label

        if headline_offer:
            object_to_index["offer"]["isHeadline"] = True
            if headline_offer.timespan.upper:
                object_to_index["offer"]["isHeadlineUntil"] = headline_offer.timespan.upper.timestamp()

        if artists:
            object_to_index["artists"] = artists

        for section in ("offer", "offerer", "venue"):
            object_to_index[section] = {
                key: value for key, value in object_to_index[section].items() if value is not None
            }

        return object_to_index

    @classmethod
    def serialize_venue(cls, venue: offerers_models.Venue) -> dict:
        social_medias = getattr(venue.contact, "social_medias", {})
        has_at_least_one_bookable_offer = offerers_api.has_venue_at_least_one_bookable_offer(venue)

        address = None
        city = None
        postalCode = None
        if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
            if venue.offererAddress is not None:
                address = venue.offererAddress.address.street
                city = venue.offererAddress.address.city
                postalCode = venue.offererAddress.address.postalCode
        else:
            address = venue.street
            city = venue.city
            postalCode = venue.postalCode

        return {
            "_geoloc": position(venue),
            "adress": address,
            "audio_disability": venue.audioDisabilityCompliant,
            "banner_url": venue.bannerUrl,
            "city": city,
            "date_created": venue.dateCreated.timestamp(),
            "description": venue.description,
            "email": getattr(venue.contact, "email", None),
            "facebook": social_medias.get("facebook"),
            "has_at_least_one_bookable_offer": has_at_least_one_bookable_offer,
            "instagram": social_medias.get("instagram"),
            "mental_disability": venue.mentalDisabilityCompliant,
            "motor_disability": venue.motorDisabilityCompliant,
            "name": venue.publicName or venue.name,
            "objectID": venue.id,
            "offerer_name": venue.managingOfferer.name,
            "phone_number": getattr(venue.contact, "phone_number", None),
            "postalCode": postalCode,
            "snapchat": social_medias.get("snapchat"),
            "tags": [criterion.name for criterion in venue.criteria],
            "twitter": social_medias.get("twitter"),
            "venue_type": venue.venueTypeCode.name,
            "visual_disability": venue.visualDisabilityCompliant,
            "website": getattr(venue.contact, "website", None),
        }

    @classmethod
    def serialize_collective_offer_template(
        cls, collective_offer_template: educational_models.CollectiveOfferTemplate
    ) -> dict:
        venue = collective_offer_template.venue
        offerer = venue.managingOfferer
        date_created = collective_offer_template.dateCreated.timestamp()

        if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
            postalCode = venue.offererAddress.address.postalCode if venue.offererAddress else None
        else:
            postalCode = venue.postalCode
        assert postalCode  # helps mypy, it would crash below if None
        # TODO(activation): why don't we just use venue.offererAddress.address.departmentCode ?
        department_code = get_department_code_from_city_code(postalCode)
        latitude, longitude = educational_api_offer.get_offer_coordinates(collective_offer_template)

        raw_formats = collective_offer_template.get_formats()
        formats = [fmt.value for fmt in raw_formats] if raw_formats else None

        return {
            "objectID": _transform_collective_offer_template_id(collective_offer_template.id),
            "offer": {
                "dateCreated": date_created,
                "name": collective_offer_template.name,
                "students": [student.value for student in collective_offer_template.students],
                "subcategoryId": collective_offer_template.subcategoryId,
                "domains": [domain.id for domain in collective_offer_template.domains],
                "educationalInstitutionUAICode": "all",
                "interventionArea": collective_offer_template.interventionArea,
                "schoolInterventionArea": (
                    collective_offer_template.interventionArea
                    if collective_offer_template.offerVenue.get("addressType") == "school"
                    else None
                ),
                "eventAddressType": collective_offer_template.offerVenue.get("addressType"),
                "beginningDatetime": date_created,  # this hack is needed to make the order keeps working
                "description": remove_stopwords(collective_offer_template.description),
            },
            "offerer": {
                "name": offerer.name,
            },
            "venue": {
                "academy": get_academy_from_department(department_code),
                "departmentCode": department_code,
                "id": venue.id,
                "name": venue.name,
                "publicName": venue.publicName,
                "adageId": venue.adageId,
            },
            "_geoloc": format_coordinates(latitude, longitude),
            "isTemplate": True,
            "formats": formats,
        }

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
            except Exception:  # pylint: disable=broad-exception-caught
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

    def search_offer_ids(self, query: str = "", count: int = 20, **params: typing.Any) -> list[int]:
        ids: list[int] = []
        for page, _count in enumerate(range(0, count, MAX_SEARCH_QUERY_COUNT)):
            # handle algolia pagination of results
            hits_per_page = min(count, count - _count, MAX_SEARCH_QUERY_COUNT)
            params["page"] = page
            params["hitsPerPage"] = hits_per_page
            try:
                results = self.algolia_offers_client.search(query, params)
            except Exception as exp:
                logger.exception(
                    "Failed to search in algolia: %s",
                    exp,
                    extra={
                        "query": query,
                        "params": params,
                    },
                )
                raise SearchError("Failed to search in algolia")

            for result in results.get("hits", []):
                object_id = result["objectID"]
                if object_id.isdigit():
                    ids.append(int(object_id))
                else:
                    # Some object id are still humanized.
                    try:
                        dehumanized_id = human_ids.dehumanize(object_id)
                        assert dehumanized_id is not None  # helps mypy
                        ids.append(dehumanized_id)
                    except human_ids.NonDehumanizableId:
                        pass

            if len(results.get("hits", [])) < hits_per_page:
                break
        return ids


def position(venue: offerers_models.Venue, offer: offers_models.Offer | None = None) -> dict[str, float]:
    latitude = None
    longitude = None
    if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
        if offer and offer.offererAddress:
            latitude = offer.offererAddress.address.latitude
            longitude = offer.offererAddress.address.longitude
        elif venue.offererAddress is not None:
            latitude = venue.offererAddress.address.latitude
            longitude = venue.offererAddress.address.longitude
    else:
        latitude = venue.latitude
        longitude = venue.longitude
    return format_coordinates(latitude, longitude)


def format_coordinates(latitude: Numeric | None, longitude: Numeric | None) -> dict[str, float]:
    return {"lat": float(latitude or DEFAULT_LATITUDE), "lng": float(longitude or DEFAULT_LONGITUDE)}


def _transform_collective_offer_template_id(collective_offer_template_id: int) -> str:
    return f"T-{collective_offer_template_id}"
