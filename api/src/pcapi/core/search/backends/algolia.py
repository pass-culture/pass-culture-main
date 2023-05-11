import enum
import logging
import re
from typing import Iterable
import urllib.parse

import algoliasearch.http.requester
import algoliasearch.search_client
from flask import current_app
import redis
import sqlalchemy as sa

from pcapi import settings
from pcapi.core.educational.academies import get_academy_from_department
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import base
from pcapi.domain.music_types import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import SHOW_TYPES_LABEL_BY_CODE
from pcapi.utils import requests
import pcapi.utils.date as date_utils
from pcapi.utils.regions import get_department_code_from_postal_code
from pcapi.utils.stopwords import STOPWORDS


logger = logging.getLogger(__name__)


REDIS_OFFER_IDS_NAME = "search:algolia:offer_ids"
REDIS_OFFER_IDS_IN_ERROR_NAME = "search:algolia:offer_ids_in_error"
REDIS_VENUE_IDS_FOR_OFFERS_NAME = "search:algolia:venue_ids_for_offers"

REDIS_VENUE_IDS_TO_INDEX = "search:algolia:venue-ids-to-index"
REDIS_VENUE_IDS_IN_ERROR_TO_INDEX = "search:algolia:venue-ids-in-error-to-index"

REDIS_COLLECTIVE_OFFER_IDS_TO_INDEX = "search:algolia:collective-offer-ids-to-index"
REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX = "search:algolia:collective-offer-template-ids-to-index"
REDIS_COLLECTIVE_OFFER_IDS_IN_ERROR_TO_INDEX = "search:algolia:collective-offer-ids-in-error-to-index"
REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX = "search:algolia:collective-offer-template-ids-in-error-to-index"
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
        self.algolia_collective_offers_client = client.init_index(settings.ALGOLIA_COLLECTIVE_OFFERS_INDEX_NAME)
        self.algolia_collective_offers_templates_client = client.init_index(
            settings.ALGOLIA_COLLECTIVE_OFFERS_INDEX_NAME
        )
        self.algolia_venues_client = client.init_index(settings.ALGOLIA_VENUES_INDEX_NAME)
        self.redis_client = current_app.redis_client  # type: ignore[attr-defined]

    def enqueue_offer_ids(self, offer_ids: Iterable[int]) -> None:
        self._enqueue_ids(offer_ids, REDIS_OFFER_IDS_NAME)

    def enqueue_offer_ids_in_error(self, offer_ids: Iterable[int]) -> None:
        self._enqueue_ids(offer_ids, REDIS_OFFER_IDS_IN_ERROR_NAME)

    def enqueue_collective_offer_ids(self, collective_offer_ids: Iterable[int]) -> None:
        self._enqueue_ids(
            collective_offer_ids,
            REDIS_COLLECTIVE_OFFER_IDS_TO_INDEX,
        )

    def enqueue_collective_offer_ids_in_error(self, collective_offer_ids: Iterable[int]) -> None:
        self._enqueue_ids(
            collective_offer_ids,
            REDIS_COLLECTIVE_OFFER_IDS_IN_ERROR_TO_INDEX,
        )

    def enqueue_collective_offer_template_ids(
        self,
        collective_offer_template_ids: Iterable[int],
    ) -> None:
        self._enqueue_ids(
            collective_offer_template_ids,
            REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX,
        )

    def enqueue_collective_offer_template_ids_in_error(
        self,
        collective_offer_template_ids: Iterable[int],
    ) -> None:
        self._enqueue_ids(
            collective_offer_template_ids,
            REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX,
        )

    def enqueue_venue_ids(self, venue_ids: Iterable[int]) -> None:
        return self._enqueue_ids(venue_ids, REDIS_VENUE_IDS_TO_INDEX)

    def enqueue_venue_ids_in_error(self, venue_ids: Iterable[int]) -> None:
        return self._enqueue_ids(venue_ids, REDIS_VENUE_IDS_IN_ERROR_TO_INDEX)

    def enqueue_venue_ids_for_offers(self, venue_ids: Iterable[int]) -> None:
        return self._enqueue_ids(venue_ids, REDIS_VENUE_IDS_FOR_OFFERS_NAME)

    def _enqueue_ids(self, ids: Iterable[int], queue_name: str) -> None:
        if not ids:
            return

        try:
            self.redis_client.sadd(queue_name, *ids)
        except redis.exceptions.RedisError:
            logger.exception("Could not add ids to indexation queue", extra={"ids": ids, "queue": queue_name})

    def pop_offer_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        if from_error_queue:
            redis_set_name = REDIS_OFFER_IDS_IN_ERROR_NAME
        else:
            redis_set_name = REDIS_OFFER_IDS_NAME

        return self._pop_ids_from_queue(count, redis_set_name)

    def pop_venue_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        if from_error_queue:
            redis_set_name = REDIS_VENUE_IDS_IN_ERROR_TO_INDEX
        else:
            redis_set_name = REDIS_VENUE_IDS_TO_INDEX

        return self._pop_ids_from_queue(count, redis_set_name)

    def pop_collective_offer_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        if from_error_queue:
            redis_set_name = REDIS_COLLECTIVE_OFFER_IDS_IN_ERROR_TO_INDEX
        else:
            redis_set_name = REDIS_COLLECTIVE_OFFER_IDS_TO_INDEX

        return self._pop_ids_from_queue(count, redis_set_name)

    def pop_collective_offer_template_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        if from_error_queue:
            redis_set_name = REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX
        else:
            redis_set_name = REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX

        return self._pop_ids_from_queue(count, redis_set_name)

    def pop_venue_ids_for_offers_from_queue(self, count: int) -> set[int]:
        return self._pop_ids_from_queue(count, REDIS_VENUE_IDS_FOR_OFFERS_NAME)

    def _pop_ids_from_queue(self, count: int, queue_name: str) -> set[int]:
        try:
            ids = self.redis_client.spop(queue_name, count)
            return {int(object_id) for object_id in ids}  # str -> int
        except redis.exceptions.RedisError:
            logger.exception("Could not pop object ids to index from queue", extra={"queue": queue_name})
            return set()

    def count_offers_to_index_from_queue(self, from_error_queue: bool = False) -> int:
        if from_error_queue:
            redis_set_name = REDIS_OFFER_IDS_IN_ERROR_NAME
        else:
            redis_set_name = REDIS_OFFER_IDS_NAME

        try:
            return self.redis_client.scard(redis_set_name)
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

    def index_offers(self, offers: Iterable[offers_models.Offer], last_30_days_bookings: dict[int, int]) -> None:
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
                pipeline.hset(REDIS_HASHMAP_INDEXED_OFFERS_NAME, offer_id, "")
            pipeline.execute()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Could not add to list of indexed offers", extra={"offers": offer_ids})
        finally:
            pipeline.reset()

    def index_collective_offers(
        self,
        collective_offers: Iterable[educational_models.CollectiveOffer],
    ) -> None:
        if not collective_offers:
            return
        objects = [self.serialize_collective_offer(collective_offer) for collective_offer in collective_offers]
        self.algolia_collective_offers_client.save_objects(objects)

    def index_collective_offer_templates(
        self,
        collective_offer_templates: Iterable[educational_models.CollectiveOfferTemplate],
    ) -> None:
        if not collective_offer_templates:
            return
        objects = [
            self.serialize_collective_offer_template(collective_offer_template)
            for collective_offer_template in collective_offer_templates
        ]
        self.algolia_collective_offers_templates_client.save_objects(objects)

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

    def unindex_collective_offer_ids(self, collective_offer_ids: Iterable[int]) -> None:
        if not collective_offer_ids:
            return
        self.algolia_collective_offers_client.delete_objects(collective_offer_ids)

    def unindex_collective_offer_template_ids(self, collective_offer_template_ids: Iterable[int]) -> None:
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

    def unindex_all_collective_offers(self, *, only_template: bool = False, only_non_template: bool = False) -> None:
        if only_template and not only_non_template:
            self.algolia_collective_offers_client.delete_by({"facetFilters": ["isTemplate:true"]})
        elif not only_template and only_non_template:
            self.algolia_collective_offers_client.delete_by({"facetFilters": ["isTemplate:false"]})
        else:
            self.algolia_collective_offers_client.clear_objects()

    def unindex_all_collective_offers_templates(self) -> None:
        self.algolia_collective_offers_templates_client.clear_objects()

    @classmethod
    def serialize_offer(cls, offer: offers_models.Offer, last_30_days_bookings: int) -> dict:
        venue = offer.venue
        offerer = venue.managingOfferer
        prices = map(lambda stock: stock.price, offer.bookableStocks)
        prices_sorted = sorted(prices, key=float)
        dates = []
        times = []
        if offer.isEvent:
            dates = [stock.beginningDatetime.timestamp() for stock in offer.bookableStocks]  # type: ignore[union-attr]
            times = [
                date_utils.get_time_in_seconds_from_datetime(stock.beginningDatetime) for stock in offer.bookableStocks  # type: ignore[arg-type]
            ]
        date_created = offer.dateCreated.timestamp()
        stocks_date_created = [stock.dateCreated.timestamp() for stock in offer.bookableStocks]
        tags = [criterion.name for criterion in offer.criteria]
        extra_data = offer.extraData or {}
        artist = " ".join(extra_data.get(key, "") for key in ("author", "performer", "speaker", "stageDirector"))  # type: ignore[misc]

        # Field used by Algolia (not the frontend) to deduplicate results
        # https://www.algolia.com/doc/api-reference/api-parameters/distinct/
        distinct = extra_data.get("isbn") or extra_data.get("visa") or extra_data.get("ean") or str(offer.id)
        distinct += extra_data.get("diffusionVersion") or ""

        music_type_label = None
        music_type = (extra_data.get("musicType") or "").strip()
        if music_type:
            try:
                music_type_label = MUSIC_TYPES_LABEL_BY_CODE[int(music_type)]
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

        object_to_index = {
            "distinct": distinct,
            "objectID": offer.id,
            "offer": {
                "artist": artist.strip() or None,
                "bookMacroSection": macro_section,
                "dateCreated": date_created,
                "dates": sorted(dates),
                "description": remove_stopwords(offer.description or ""),
                "isDigital": offer.isDigital,
                "isDuo": offer.isDuo,
                "isEducational": False,
                "isEvent": offer.isEvent,
                "isForbiddenToUnderage": offer.is_forbidden_to_underage,
                "isThing": offer.isThing,
                "last30DaysBookings": last_30_days_bookings,
                "last30DaysBookingsRange": get_last_30_days_bookings_range(last_30_days_bookings),
                "movieGenres": extra_data.get("genres"),
                "musicType": music_type_label,
                "name": offer.name,
                "nativeCategoryId": offer.subcategory.native_category_id,
                "prices": prices_sorted,
                # TODO(jeremieb): keep searchGroupNamev2 and remove
                # remove searchGroupName once the search group name &
                # home page label migration is over.
                "rankingWeight": offer.rankingWeight,
                "searchGroupName": offer.subcategory.search_group_name,
                "searchGroupNamev2": offer.subcategory_v2.search_group_name,
                "showType": show_type_label,
                "stocksDateCreated": sorted(stocks_date_created),
                "students": extra_data.get("students") or [],
                "subcategoryId": offer.subcategory.id,
                "thumbUrl": url_path(offer.thumbUrl),
                "tags": tags,
                "times": list(set(times)),
            },
            "offerer": {
                "name": offerer.name,
            },
            "venue": {
                "address": venue.address,
                "city": venue.city,
                "departmentCode": venue.departementCode,
                "id": venue.id,
                "name": venue.name,
                "postalCode": venue.postalCode,
                "publicName": venue.publicName,
            },
            "_geoloc": position(venue),
        }

        return object_to_index

    @classmethod
    def serialize_venue(cls, venue: offerers_models.Venue) -> dict:
        social_medias = getattr(venue.contact, "social_medias", {})
        has_at_least_one_bookable_offer = offerers_api.has_venue_at_least_one_bookable_offer(venue)

        return {
            "objectID": venue.id,
            "city": venue.city,
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
            "tags": [criterion.name for criterion in venue.criteria],
            "banner_url": venue.bannerUrl,
            "_geoloc": position(venue),
            "has_at_least_one_bookable_offer": has_at_least_one_bookable_offer,
        }

    @classmethod
    def serialize_collective_offer(cls, collective_offer: educational_models.CollectiveOffer) -> dict:
        venue = collective_offer.venue
        offerer = venue.managingOfferer
        date_created = collective_offer.dateCreated.timestamp()
        beginning_datetime = collective_offer.collectiveStock.beginningDatetime.timestamp()
        department_code = get_department_code_from_postal_code(venue.postalCode)

        return {
            "objectID": collective_offer.id,
            "offer": {
                "dateCreated": date_created,
                "name": collective_offer.name,
                "students": [student.value for student in collective_offer.students],
                "subcategoryId": collective_offer.subcategoryId,
                "domains": [domain.id for domain in collective_offer.domains],
                "educationalInstitutionUAICode": collective_offer.institution.institutionId
                if collective_offer.institution
                else "all",
                "interventionArea": collective_offer.interventionArea,
                "schoolInterventionArea": collective_offer.interventionArea
                if collective_offer.offerVenue.get("addressType") == "school"
                else None,
                "eventAddressType": collective_offer.offerVenue.get("addressType"),
                "beginningDatetime": beginning_datetime,
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
            },
            "_geoloc": {
                "lat": venue.latitude,
                "lng": venue.longitude,
            },
            "isTemplate": False,
        }

    @classmethod
    def serialize_collective_offer_template(
        cls, collective_offer_template: educational_models.CollectiveOfferTemplate
    ) -> dict:
        venue = collective_offer_template.venue
        offerer = venue.managingOfferer
        date_created = collective_offer_template.dateCreated.timestamp()
        department_code = get_department_code_from_postal_code(venue.postalCode)

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
                "schoolInterventionArea": collective_offer_template.interventionArea
                if collective_offer_template.offerVenue.get("addressType") == "school"
                else None,
                "eventAddressType": collective_offer_template.offerVenue.get("addressType"),
                "beginningDatetime": date_created,  # this hack is needed to make the order keeps working
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
            },
            "_geoloc": {
                "lat": venue.latitude,
                "lng": venue.longitude,
            },
            "isTemplate": True,
        }


def position(venue: offerers_models.Venue) -> dict[str, float]:
    latitude = venue.latitude or DEFAULT_LATITUDE
    longitude = venue.longitude or DEFAULT_LONGITUDE
    return {"lat": float(latitude), "lng": float(longitude)}


def _transform_collective_offer_template_id(collective_offer_template_id: int) -> str:
    return f"T-{collective_offer_template_id}"
