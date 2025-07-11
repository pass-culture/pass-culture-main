import datetime
import decimal
import enum
import logging
import re
import typing
import urllib.parse

import sqlalchemy as sa

from pcapi import settings
from pcapi.core.artist import models as artists_models
from pcapi.core.categories import pro_categories
from pcapi.core.categories.app_search_tree import NATIVE_CATEGORIES
from pcapi.core.categories.app_search_tree import SEARCH_GROUPS
from pcapi.core.categories.genres.music import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.music import TITELIVE_MUSIC_TYPES
from pcapi.core.categories.models import SHOW_TYPES_LABEL_BY_CODE
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.academies import get_academy_from_department
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.geography import api as geography_api
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.utils import get_offer_address
from pcapi.core.providers import constants as provider_constants
from pcapi.core.providers import titelive_gtl
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.models import db
from pcapi.models import feature
from pcapi.utils import date as date_utils
from pcapi.utils.stopwords import STOPWORDS


logger = logging.getLogger(__name__)

DEFAULT_LONGITUDE = 2.409289
DEFAULT_LATITUDE = 47.158459


WORD_SPLITTER = re.compile(r"\W+")


Numeric = float | decimal.Decimal


class Last30DaysBookingsRange(enum.Enum):
    VERY_LOW = "very-low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very-high"


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


class AlgoliaSerializationMixin:
    @classmethod
    def serialize_artist(cls, artist: artists_models.Artist) -> dict:
        return {
            "objectID": artist.id,
            "description": artist.description,
            "image": artist.image,
            "name": artist.name,
        }

    @classmethod
    def serialize_offer(cls, offer: offers_models.Offer, last_30_days_bookings: int) -> dict:
        venue = offer.venue
        offerer = venue.managingOfferer
        prices = {stock.price for stock in offer.searchableStocks}
        dates = set()
        times = set()
        if offer.isEvent:
            dates = {stock.beginningDatetime.timestamp() for stock in offer.searchableStocks}  # type: ignore[union-attr]
            times = {
                date_utils.get_time_in_seconds_from_datetime(stock.beginningDatetime)  # type: ignore[arg-type]
                for stock in offer.searchableStocks
            }
        date_created = offer.dateCreated.timestamp()
        tags = [criterion.name for criterion in offer.criteria]

        extra_data = offer.product.extraData if offer.product and offer.product.extraData else offer.extraData or {}

        extra_data_artists = []
        for key in ("author", "performer", "speaker", "stageDirector"):
            artist = str(extra_data.get(key) or "")
            if _is_artist_valid(artist):
                extra_data_artists.append(artist)

        artists = (
            [
                {"id": artist.id, "image": artist.image or offer.thumbUrl, "name": artist.name}
                for artist in offer.product.artists
            ]
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
            str(extra_data.get("allocineId", ""))
            or extra_data.get("visa")
            or (offer.product.ean if offer.product else offer.ean)
            or str(offer.id)
        )
        gtl_id = extra_data.get("gtl_id")

        try:
            book_format = provider_constants.BookFormat[extra_data.get("bookFormat") or ""].value
        except KeyError:
            book_format = None

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
                    db.session.query(offers_models.BookMacroSection)
                    .filter(sa.func.lower(offers_models.BookMacroSection.section) == section)
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

        search_groups = [
            search_group.search_value
            for search_group in SEARCH_GROUPS
            if offer.subcategory.id in search_group.included_subcategories
        ]

        native_categories = [
            native_category.search_value
            for native_category in NATIVE_CATEGORIES
            if offer.subcategory.id in native_category.included_subcategories
        ]

        headline_offer = next(
            (headline_offer for headline_offer in offer.headlineOffers if headline_offer.isActive), None
        )

        chronicles_count = (
            offer.product.chroniclesCount if offer.product and offer.product.chroniclesCount else offer.chroniclesCount
        )
        headlines_count = offer.product.headlinesCount if offer.product and offer.product.headlinesCount else None
        likes_count = offer.product.likesCount if offer.product and offer.product.likesCount else offer.likesCount
        # If you update this dictionary, please check whether you need to
        # also update `core.offerers.api.VENUE_ALGOLIA_INDEXED_FIELDS`.
        object_to_index: dict[str, typing.Any] = {
            "distinct": distinct,
            "objectID": offer.id,
            "offer": {
                "allocineId": extra_data.get("allocineId"),
                "artist": " ".join(extra_data_artists).strip() or None,
                "chroniclesCount": chronicles_count or None,
                "bookMacroSection": macro_section,
                "dateCreated": date_created,
                "dates": sorted(dates),
                "description": remove_stopwords(offer.description or ""),
                "ean": offer.ean,
                "gtlCodeLevel1": gtl_code_1,
                "gtlCodeLevel2": gtl_code_2,
                "gtlCodeLevel3": gtl_code_3,
                "gtlCodeLevel4": gtl_code_4,
                "headlinesCount": headlines_count or None,
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
                "likes": likes_count or None,
                "movieGenres": extra_data.get("genres"),
                "musicType": music_type_labels,
                "name": offer.name,
                "nativeCategoryId": native_categories,
                "prices": sorted(prices),
                "publicationDate": (
                    offer.publicationDate.timestamp() if offer.publicationDate and not offer.isReleased else None
                ),
                "rankingWeight": offer.rankingWeight,
                "releaseDate": release_date,
                "bookFormat": book_format,
                # TODO(thconte, 2025-12-23): keep searchGroups and remove
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
                "name": venue.common_name,
                "postalCode": postal_code,
                "publicName": venue.publicName,
                "venue_type": venue.venueTypeCode.name,
            },
            "_geoloc": position(venue, offer),
        }

        if offer.subcategory.category.id == pro_categories.LIVRE.id and gtl:
            object_to_index["offer"]["gtl_level1"] = gtl.get("level_01_label")
            object_to_index["offer"]["gtl_level2"] = gtl.get("level_02_label")
            object_to_index["offer"]["gtl_level3"] = gtl.get("level_03_label")
            object_to_index["offer"]["gtl_level4"] = gtl.get("level_04_label")
        elif gtl_id and offer.subcategory.category.id in (
            pro_categories.MUSIQUE_ENREGISTREE.id,
            pro_categories.MUSIQUE_LIVE.id,
        ):
            gtl_label = next(
                (music_type.label for music_type in TITELIVE_MUSIC_TYPES if music_type.gtl_id == gtl_id),
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
        if venue.offererAddress is not None:
            address = venue.offererAddress.address.street
            city = venue.offererAddress.address.city
            postalCode = venue.offererAddress.address.postalCode

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
            "name": venue.common_name,
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

        if venue.offererAddress is not None:
            department_code = venue.offererAddress.address.departmentCode
        else:
            # TODO(OA): remove this when the virtual venues are migrated
            department_code = None

        if feature.FeatureToggle.WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE.is_active():
            coordinates = _get_collective_offer_template_coordinates_from_address(collective_offer_template)
        else:
            coordinates = _get_collective_offer_template_coordinates_from_offer_venue(collective_offer_template)

        latitude, longitude = (coordinates.latitude, coordinates.longitude) if coordinates is not None else (None, None)

        return {
            "objectID": _transform_collective_offer_template_id(collective_offer_template.id),
            "offer": {
                "dateCreated": date_created,
                "name": collective_offer_template.name,
                "students": [student.value for student in collective_offer_template.students],
                "domains": [domain.id for domain in collective_offer_template.domains],
                "interventionArea": collective_offer_template.interventionArea,
                "schoolInterventionArea": (
                    collective_offer_template.interventionArea
                    if collective_offer_template.offerVenue.get("addressType") == "school"
                    else None
                ),
                "eventAddressType": collective_offer_template.offerVenue.get("addressType"),
                "locationType": (
                    collective_offer_template.locationType.value if collective_offer_template.locationType else None
                ),
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
            "formats": [format.value for format in collective_offer_template.formats],
        }


def position(venue: offerers_models.Venue, offer: offers_models.Offer | None = None) -> dict[str, float]:
    latitude = None
    longitude = None
    if offer and offer.offererAddress:
        latitude = offer.offererAddress.address.latitude
        longitude = offer.offererAddress.address.longitude
    elif venue.offererAddress is not None:
        latitude = venue.offererAddress.address.latitude
        longitude = venue.offererAddress.address.longitude
    else:
        # FIXME (dramelet, 03/02/2025): This can be removed once Venue table is sanizized
        # and location columns dropped
        latitude = venue.latitude
        longitude = venue.longitude
    return format_coordinates(latitude, longitude)


def _get_collective_offer_template_coordinates_from_offer_venue(
    offer: educational_models.CollectiveOfferTemplate,
) -> geography_models.Coordinates | None:
    # use the specified venue if any or use the offer's billing address as the default
    venue = educational_api_offer.get_offer_event_venue(offer)
    return geography_api.get_coordinates(venue)


def _get_collective_offer_template_coordinates_from_address(
    offer: educational_models.CollectiveOfferTemplate,
) -> geography_models.Coordinates | None:
    match offer.locationType:
        case educational_models.CollectiveLocationType.SCHOOL | educational_models.CollectiveLocationType.TO_BE_DEFINED:
            return geography_api.get_coordinates(offer.venue)

        case educational_models.CollectiveLocationType.ADDRESS:
            return geography_api.get_coordinates(offer)

        case _:
            logger.error(f"Invalid locationType for collective offer template {offer.id}")
            return geography_api.get_coordinates(offer.venue)


def format_coordinates(latitude: Numeric | None, longitude: Numeric | None) -> dict[str, float]:
    return {"lat": float(latitude or DEFAULT_LATITUDE), "lng": float(longitude or DEFAULT_LONGITUDE)}


def _transform_collective_offer_template_id(collective_offer_template_id: int) -> str:
    return f"T-{collective_offer_template_id}"


def _is_artist_valid(artist: str) -> bool:
    return (
        bool(artist) and "," not in artist and ";" not in artist and artist.lower() not in ("collectif", "collectifs")
    )
