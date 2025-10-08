import datetime
import decimal
import enum
import logging
import typing

from pcapi import settings
from pcapi.core.external_bookings.boost import serializers as boost_serializers
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.boost.client import get_pcu_pricing_if_exists
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.providers import exceptions
from pcapi.core.providers import models


logger = logging.getLogger(__name__)


class ShowtimeFeatures(enum.Enum):
    VF = "VF"
    VO = "VO"
    THREE_D = "3D"
    ICE = "ICE"


class ExtractResult(typing.TypedDict):
    price_category_labels: list[offers_models.PriceCategoryLabel]
    cinema_attributes: list[boost_serializers.CinemaAttribut]
    showtimes: list[boost_serializers.ShowTime4]


class ShowStockData(typing.TypedDict):
    datetime: datetime.datetime
    remaining_quantity: int
    features: list
    price: decimal.Decimal
    price_label: str


class LoadableData(typing.TypedDict):
    movie_uuid: str
    movie_data: offers_models.Movie
    stocks_data: list[ShowStockData]


class BoostETLProcess:
    """
    Integration to import products, offers, stocks & price_categories for a `Venue`
    linked to `Boost`.

    It is a ETL process :
        - step 1: Extract data from Boost API
        - step 2: Transform data into a format easily loadable in our DB
        - step 3: Load transformed data into our DB
    """

    def __init__(self, venue_provider: models.VenueProvider):
        """
        :venue_provider: must be linked to Boost provider
        """
        self.venue_provider = venue_provider
        assert venue_provider.venueIdAtOfferProvider  # to make mypy happy
        self.api_client = BoostClientAPI(
            venue_provider.venueIdAtOfferProvider,
            request_timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
        )

    def _extract(self) -> ExtractResult:
        """
        Step 1: Fetch API & DB data
        """
        try:
            # api
            cinema_attributes = self.api_client.get_cinemas_attributs()
            showtimes = self.api_client.get_showtimes()
            # db
            price_category_labels = offers_repository.get_venue_price_category_labels(self.venue_provider.venueId)
        except Exception as exc:
            self._log("warning", "Step 1 - Extract failed", {"exc": exc.__class__.__name__})
            raise

        return {
            "cinema_attributes": cinema_attributes,
            "showtimes": showtimes,
            "price_category_labels": price_category_labels,
        }

    def _transform(self, extract_result: ExtractResult) -> list[LoadableData]:
        """
        Step 2: Make data easily loadable
        """
        loadable_data_by_movie_uuid: dict[str, LoadableData] = {}

        ice_immersive_attribute_id = self._get_ice_immersive_attribute_id(extract_result["cinema_attributes"])

        for showtime in extract_result["showtimes"]:
            pass_culture_pricing = get_pcu_pricing_if_exists(showtime.showtimePricing)

            if not pass_culture_pricing:
                self._log(
                    "warning",
                    "Step 2 - Missing pass Culture pricing",
                    {
                        "id": showtime.id,
                        "date": showtime.showDate,
                        "film": {
                            "id": showtime.film.id,
                            "title": showtime.film.titleCnc,
                        },
                    },
                )
                continue

            movie_uuid = _build_movie_uuid(showtime.film.id, self.venue_provider.venue)
            show_stock_data = self._transform_showtime_to_show_stock_data(
                showtime,
                pass_culture_pricing,
                ice_immersive_attribute_id,
            )

            if movie_uuid in loadable_data_by_movie_uuid:
                loadable_data_by_movie_uuid[movie_uuid]["stocks_data"].append(show_stock_data)
            else:
                loadable_data_by_movie_uuid[movie_uuid] = {
                    "stocks_data": [show_stock_data],
                    "movie_data": showtime.film.to_generic_movie(),
                    "movie_uuid": movie_uuid,
                }
        return list(loadable_data_by_movie_uuid.values())

    def _get_ice_immersive_attribute_id(self, cinema_attributes: list[boost_serializers.CinemaAttribut]) -> int | None:
        for cinema_attribute in cinema_attributes:
            if cinema_attribute.title == ShowtimeFeatures.ICE.value:
                return cinema_attribute.id
        return None

    def _transform_showtime_to_show_stock_data(
        self,
        showtime: boost_serializers.ShowTime4,
        pass_culture_pricing: boost_serializers.ShowtimePricing,
        ice_immersive_attribute_id: int | None,
    ) -> ShowStockData:
        features = []

        if ShowtimeFeatures.VO.value == showtime.version["code"]:
            features.append(ShowtimeFeatures.VO.value)
        elif ShowtimeFeatures.VF.value == showtime.version["code"]:
            features.append(ShowtimeFeatures.VF.value)

        if ShowtimeFeatures.THREE_D.value == showtime.format["title"]:
            features.append(ShowtimeFeatures.THREE_D.value)

        if ice_immersive_attribute_id is not None and ice_immersive_attribute_id in showtime.attributs:
            features.append(ShowtimeFeatures.ICE.value)

        return {
            "datetime": showtime.showDate,
            "price": pass_culture_pricing.amountTaxesIncluded,
            "price_label": pass_culture_pricing.title,
            "remaining_quantity": showtime.numberSeatsRemaining,
            "features": features,
        }

    def execute(self) -> None:
        """
        Check provider & venue_provider are active, then execute the etl process (extract, transform, load)

        :raise: `InactiveProvider`, `InactiveVenueProvider`
        """
        # Check provider and venue_provider are active
        if not self.venue_provider.provider.isActive:
            self._log("warning", "Init - Provider inactive")
            raise exceptions.InactiveProvider()
        if not self.venue_provider.isActive:
            self._log("warning", "Init - VenueProvider inactive")
            raise exceptions.InactiveVenueProvider()

        # Step 1 : Extract (API calls)
        result = self._extract()

        self._log(
            "debug",
            "Step 1 - Extract done",
            {
                "cinema_attributes": [cinema_attribute.dict() for cinema_attribute in result["cinema_attributes"]],
                "showtimes": [showtime.dict() for showtime in result["showtimes"]],
                "price_category_labels": result["price_category_labels"],
            },
        )

        # Step 2 : Transform
        transform_result = self._transform(result)

        self._log("debug", " Step 2 - Transform done", transform_result)

    def _log(self, level: str, message: str, data: dict | list | None = None) -> None:
        log_message = "[%s] %s" % (self.__class__.__name__, message)
        extra: dict = {
            "venue_id": self.venue_provider.venueId,
            "provider_id": self.venue_provider.providerId,
            "venue_provider_id": self.venue_provider.id,
            "venue_id_at_offer_provider": self.venue_provider.venueIdAtOfferProvider,
        }
        if data:
            extra["log_data"] = data

        if level == "warning":
            logger.warning(log_message, extra=extra)
        elif level == "debug":
            logger.debug(log_message, extra=extra)


def _build_movie_uuid(film_id: int, venue: offerers_models.Venue) -> str:
    return f"{film_id}%{venue.id}%Boost"
