from datetime import datetime
import decimal
import re

from dateutil.parser import parse

from pcapi import settings
from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
import pcapi.core.providers.models as providers_models
from pcapi.domain.allocine import get_movie_poster
from pcapi.domain.allocine import get_movies_showtimes
from pcapi.domain.price_rule import AllocineStocksPriceRule
from pcapi.domain.price_rule import PriceRule
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.utils.date import get_department_timezone
from pcapi.utils.date import local_datetime_to_default_timezone


DIGITAL_PROJECTION = "DIGITAL"
DUBBED_VERSION = "DUBBED"
LOCAL_VERSION = "LOCAL"
ORIGINAL_VERSION = "ORIGINAL"
FRENCH_VERSION_SUFFIX = "VF"
ORIGINAL_VERSION_SUFFIX = "VO"


class AllocineStocks(LocalProvider):
    name = "Allociné"
    can_create = True

    def __init__(self, allocine_venue_provider: providers_models.AllocineVenueProvider):
        super().__init__(allocine_venue_provider)
        self.api_key = settings.ALLOCINE_API_KEY
        self.venue = allocine_venue_provider.venue
        self.theater_id = allocine_venue_provider.venueIdAtOfferProvider
        self.movies_showtimes = get_movies_showtimes(self.api_key, self.theater_id)
        self.isDuo = allocine_venue_provider.isDuo
        self.quantity = allocine_venue_provider.quantity
        self.room_internal_id = allocine_venue_provider.internalId
        self.price_and_price_rule_tuples: list[tuple[decimal.Decimal, PriceRule]] = (
            providers_models.AllocineVenueProviderPriceRule.query.filter(
                providers_models.AllocineVenueProviderPriceRule.allocineVenueProvider == allocine_venue_provider
            )
            .with_entities(
                providers_models.AllocineVenueProviderPriceRule.price,
                providers_models.AllocineVenueProviderPriceRule.priceRule,
            )
            .all()
        )

        self.movie_information: dict | None = None
        self.filtered_movie_showtimes: list[dict] | None = None
        self.last_product_id: int | None = None
        self.last_vf_offer_id: int | None = None
        self.last_vo_offer_id: int | None = None
        self.label: offers_models.PriceCategoryLabel = offers_api.get_or_create_label("Tarif unique", self.venue)
        self.price_categories_by_offer: dict[offers_models.Offer, list[offers_models.PriceCategory]] = {}

    def __next__(self) -> list[ProvidableInfo]:
        raw_movie_information = next(self.movies_showtimes)  # type: ignore [var-annotated]
        try:
            self.movie_information = retrieve_movie_information(raw_movie_information["node"]["movie"])
            self.filtered_movie_showtimes = _filter_only_digital_and_non_experience_showtimes(
                raw_movie_information["node"]["showtimes"]
            )
        except (KeyError, TypeError):
            self.log_provider_event(
                providers_models.LocalProviderEventType.SyncError,
                f"Error parsing movie for theater {self.venue.siret}",
            )
            return []

        showtimes_number = len(self.filtered_movie_showtimes)
        providable_information_list = [
            self.create_providable_info(
                offers_models.Product, self.movie_information["id"], datetime.utcnow(), self.movie_information["id"]
            )
        ]

        if _has_original_version_product(self.filtered_movie_showtimes):
            venue_movie_original_version_unique_id = _build_original_movie_uuid(self.movie_information, self.venue)
            original_version_offer_providable_information = self.create_providable_info(
                offers_models.Offer,
                venue_movie_original_version_unique_id,
                datetime.utcnow(),
                venue_movie_original_version_unique_id,
            )

            providable_information_list.append(original_version_offer_providable_information)

        if _has_french_version_product(self.filtered_movie_showtimes):
            venue_movie_french_version_unique_id = _build_french_movie_uuid(self.movie_information, self.venue)
            french_version_offer_providable_information = self.create_providable_info(
                offers_models.Offer,
                venue_movie_french_version_unique_id,
                datetime.utcnow(),
                venue_movie_french_version_unique_id,
            )
            providable_information_list.append(french_version_offer_providable_information)

        for showtime_number in range(showtimes_number):
            showtime = self.filtered_movie_showtimes[showtime_number]
            id_at_providers = _build_stock_uuid(self.movie_information, self.venue, showtime)

            stock_providable_information = self.create_providable_info(
                offers_models.Stock, id_at_providers, datetime.utcnow(), id_at_providers
            )
            providable_information_list.append(stock_providable_information)

        return providable_information_list

    def fill_object_attributes(self, pc_object: Model) -> None:
        if isinstance(pc_object, offers_models.Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, offers_models.Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, offers_models.Stock):
            self.fill_stock_attributes(pc_object)

    def update_from_movie_information(
        self, obj: offers_models.Offer | offers_models.Product, movie_information: dict
    ) -> None:
        if self.movie_information and "description" in self.movie_information:
            obj.description = movie_information["description"]
        if self.movie_information and "duration" in self.movie_information:
            obj.durationMinutes = movie_information["duration"]
        if not obj.extraData:
            obj.extraData = {}
        for field in (
            "visa",
            "stageDirector",
            "genres",
            "type",
            "companies",
            "releaseDate",
            "countries",
            "cast",
        ):
            if field in movie_information:
                # FIXME (2023-03-16): Currently not supported by mypy https://github.com/python/mypy/issues/7178
                obj.extraData[field] = movie_information[field]  # type: ignore [literal-required, index]

    def fill_product_attributes(self, allocine_product: offers_models.Product) -> None:
        allocine_product.name = self.movie_information["title"]  # type: ignore [index]
        allocine_product.subcategoryId = subcategories.SEANCE_CINE.id

        self.update_from_movie_information(allocine_product, self.movie_information)  # type: ignore [arg-type]

        is_new_product_to_insert = allocine_product.id is None
        if is_new_product_to_insert:
            allocine_product.id = offers_repository.get_next_product_id_from_database()

        self.last_product = allocine_product

    def fill_offer_attributes(self, allocine_offer: offers_models.Offer) -> None:
        allocine_offer.venueId = self.venue.id
        allocine_offer.bookingEmail = self.venue.bookingEmail
        allocine_offer.withdrawalDetails = self.venue.withdrawalDetails

        self.update_from_movie_information(allocine_offer, self.movie_information)  # type: ignore [arg-type]

        if allocine_offer.extraData is None:
            allocine_offer.extraData = {}
        allocine_offer.extraData["theater"] = {  # type: ignore [index]
            "allocine_movie_id": self.movie_information["internal_id"],  # type: ignore [index]
            "allocine_room_id": self.room_internal_id,
        }

        if self.movie_information and "visa" in self.movie_information:
            allocine_offer.extraData["visa"] = self.movie_information["visa"]  # type: ignore [index]
        if self.movie_information and "stageDirector" in self.movie_information:
            allocine_offer.extraData["stageDirector"] = self.movie_information["stageDirector"]  # type: ignore [index]

        movie_version = (
            ORIGINAL_VERSION_SUFFIX
            if _is_original_version_offer(allocine_offer.idAtProvider)  # type: ignore [arg-type]
            else FRENCH_VERSION_SUFFIX
        )

        allocine_offer.name = f"{self.movie_information['title']} - {movie_version}"  # type: ignore [index]
        allocine_offer.subcategoryId = subcategories.SEANCE_CINE.id
        allocine_offer.product = self.last_product
        allocine_offer.extraData["diffusionVersion"] = movie_version  # type: ignore [index]

        is_new_offer_to_insert = allocine_offer.id is None
        if is_new_offer_to_insert:
            allocine_offer.isDuo = self.isDuo

        if movie_version == ORIGINAL_VERSION_SUFFIX:
            self.last_vo_offer = allocine_offer
        else:
            self.last_vf_offer = allocine_offer

    def fill_stock_attributes(self, allocine_stock: offers_models.Stock) -> None:
        showtime_uuid = _get_showtimes_uuid_by_idAtProvider(allocine_stock.idAtProviders)  # type: ignore [arg-type]
        showtime = _find_showtime_by_showtime_uuid(self.filtered_movie_showtimes, showtime_uuid)  # type: ignore [arg-type]

        parsed_showtimes = retrieve_showtime_information(showtime)  # type: ignore [arg-type]
        diffusion_version = parsed_showtimes["diffusionVersion"]

        allocine_stock.offer = self.last_vo_offer if diffusion_version == ORIGINAL_VERSION else self.last_vf_offer

        local_tz = get_department_timezone(self.venue.departementCode)
        date_in_utc = local_datetime_to_default_timezone(parsed_showtimes["startsAt"], local_tz)
        allocine_stock.beginningDatetime = date_in_utc

        is_new_stock_to_insert = allocine_stock.id is None
        if is_new_stock_to_insert:
            allocine_stock.fieldsUpdated = []

        if "bookingLimitDatetime" not in allocine_stock.fieldsUpdated:
            allocine_stock.bookingLimitDatetime = date_in_utc

        if "quantity" not in allocine_stock.fieldsUpdated:
            allocine_stock.quantity = self.quantity

        if "price" not in allocine_stock.fieldsUpdated:
            price = self.apply_allocine_price_rule(allocine_stock)
            if allocine_stock.priceCategory is None:
                allocine_stock.price = price
                allocine_stock.priceCategory = self.get_or_create_allocine_price_category(price, allocine_stock)

            if allocine_stock.priceCategory.label == "Tarif unique":
                allocine_stock.price = price
                allocine_stock.priceCategory.price = price

    def get_or_create_allocine_price_category(
        self, price: decimal.Decimal, allocine_stock: offers_models.Stock
    ) -> offers_models.PriceCategory:
        offer = allocine_stock.offer
        if not offer in self.price_categories_by_offer:
            self.price_categories_by_offer[offer] = (
                offers_models.PriceCategory.query.filter_by(offer=offer)
                .order_by(offers_models.PriceCategory.id.desc())
                .all()
                if offer.id
                else []
            )
        price_categories = (category for category in self.price_categories_by_offer[offer] if category.price == price)
        price_category = next(price_categories, None)
        if price_category:
            return price_category

        price_category = offers_models.PriceCategory(priceCategoryLabel=self.label, price=price, offer=offer)
        self.price_categories_by_offer[offer].insert(0, price_category)
        return price_category

    def apply_allocine_price_rule(self, allocine_stock: offers_models.Stock) -> decimal.Decimal:
        for price, price_rule in self.price_and_price_rule_tuples:
            if price_rule(allocine_stock):
                return price
        raise AllocineStocksPriceRule("Aucun prix par défaut n'a été trouvé")

    def get_object_thumb(self) -> bytes:
        if "poster_url" in self.movie_information:  # type: ignore [operator]
            image_url = self.movie_information["poster_url"]  # type: ignore [index]
            return get_movie_poster(image_url)
        return bytes()

    def shall_synchronize_thumbs(self) -> bool:
        return True


def retrieve_movie_information(raw_movie_information: dict) -> dict:
    parsed_movie_information = {}
    parsed_movie_information["id"] = raw_movie_information["id"]
    parsed_movie_information["title"] = raw_movie_information["title"]
    parsed_movie_information["internal_id"] = raw_movie_information["internalId"]
    parsed_movie_information["genres"] = raw_movie_information["genres"]
    parsed_movie_information["type"] = raw_movie_information["type"]
    parsed_movie_information["companies"] = raw_movie_information["companies"]

    try:
        parsed_movie_information["description"] = _build_description(raw_movie_information)
        parsed_movie_information["duration"] = _parse_movie_duration(raw_movie_information["runtime"])
        parsed_movie_information["poster_url"] = _format_poster_url(raw_movie_information["poster"]["url"])
        parsed_movie_information["stageDirector"] = _build_stage_director_full_name(raw_movie_information)
        parsed_movie_information["visa"] = _get_operating_visa(raw_movie_information)
        parsed_movie_information["releaseDate"] = _get_release_date(raw_movie_information)
        parsed_movie_information["countries"] = _build_countries_list(raw_movie_information)
        parsed_movie_information["cast"] = _build_cast_list(raw_movie_information)

    except (TypeError, KeyError, IndexError):
        pass

    return parsed_movie_information


def retrieve_showtime_information(showtime_information: dict) -> dict:
    return {
        "startsAt": parse(showtime_information["startsAt"]),
        "diffusionVersion": showtime_information["diffusionVersion"],
        "projection": showtime_information["projection"][0],
        "experience": showtime_information["experience"],
    }


def _filter_only_digital_and_non_experience_showtimes(showtimes_information: list[dict]) -> list[dict]:
    return list(
        filter(
            lambda showtime: showtime["projection"]
            and showtime["projection"][0] == DIGITAL_PROJECTION
            and showtime["experience"] is None,
            showtimes_information,
        )
    )


def _find_showtime_by_showtime_uuid(showtimes: list[dict], showtime_uuid: str) -> dict | None:
    for showtime in showtimes:
        if _build_showtime_uuid(showtime) == showtime_uuid:
            return showtime
    return None


def _get_showtimes_uuid_by_idAtProvider(id_at_provider: str) -> str:
    return id_at_provider.split("#")[1]


def _build_description(movie_info: dict) -> str:
    allocine_movie_url = movie_info["backlink"]["url"].replace("\\", "")
    return f"{movie_info['synopsis']}\n{movie_info['backlink']['label']}: {allocine_movie_url}"


def _format_poster_url(url: str) -> str:
    return url.replace(r"\/", "/")


def _get_operating_visa(movie_info: dict) -> str | None:
    return movie_info["releases"][0]["data"]["visa_number"]


def _build_stage_director_full_name(movie_info: dict) -> str:
    stage_director_first_name = movie_info["credits"]["edges"][0]["node"]["person"]["firstName"]
    stage_director_last_name = movie_info["credits"]["edges"][0]["node"]["person"]["lastName"]
    return f"{stage_director_first_name} {stage_director_last_name}"


def _parse_movie_duration(duration: str | None) -> int | None:
    if not duration:
        return None
    hours_minutes = "([0-9]+)H([0-9]+)"
    duration_regex = re.compile(hours_minutes)
    match = duration_regex.search(duration)
    movie_duration_hours = int(match.groups()[0])  # type: ignore [union-attr]
    movie_duration_minutes = int(match.groups()[1])  # type: ignore [union-attr]
    return movie_duration_hours * 60 + movie_duration_minutes


def _has_original_version_product(movies_showtimes: list[dict]) -> bool:
    return ORIGINAL_VERSION in list(map(lambda movie: movie["diffusionVersion"], movies_showtimes))


def _has_french_version_product(movies_showtimes: list[dict]) -> bool:
    movies = list(map(lambda movie: movie["diffusionVersion"], movies_showtimes))
    return LOCAL_VERSION in movies or DUBBED_VERSION in movies


def _is_original_version_offer(id_at_provider: str) -> bool:
    return id_at_provider[-3:] == f"-{ORIGINAL_VERSION_SUFFIX}"


def _build_movie_uuid(movie_information: dict, venue: Venue) -> str:
    venue_id = venue.id if not venue.siret else venue.siret
    return f"{movie_information['id']}%{venue_id}"


def _build_french_movie_uuid(movie_information: dict, venue: Venue) -> str:
    return f"{_build_movie_uuid(movie_information, venue)}-{FRENCH_VERSION_SUFFIX}"


def _build_original_movie_uuid(movie_information: dict, venue: Venue) -> str:
    return f"{_build_movie_uuid(movie_information, venue)}-{ORIGINAL_VERSION_SUFFIX}"


def _build_showtime_uuid(showtime_details: dict) -> str:
    return f"{showtime_details['diffusionVersion']}/{showtime_details['startsAt']}"


def _build_stock_uuid(movie_information: dict, venue: Venue, showtime_details: dict) -> str:
    return f"{_build_movie_uuid(movie_information, venue)}#{_build_showtime_uuid(showtime_details)}"


def _build_countries_list(movie_info: dict) -> list[str]:
    return [country["name"] for country in movie_info["countries"]]


def _build_cast_list(movie_info: dict) -> list[str | None]:
    cast_list = []
    edges = movie_info["cast"]["edges"]
    for edge in edges:
        actor = edge["node"]["actor"]
        first_name = actor.get("firstName", "") if actor else ""
        last_name = actor.get("lastName", "") if actor else ""
        full_name = f"{first_name} {last_name}".strip()
        if full_name:
            cast_list.append(full_name)
    return cast_list  # type: ignore [return-value]


def _get_release_date(movie_info: dict) -> str:
    return movie_info["releases"][0]["releaseDate"]["date"]
