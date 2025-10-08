import datetime
import decimal
import enum
import logging
import typing

from pcapi import settings
from pcapi.core.external_bookings.boost import serializers as boost_serializers
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.boost.client import get_pcu_pricing_if_exists
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import exceptions
from pcapi.core.providers import models


logger = logging.getLogger(__name__)


class ShowFeatures(enum.StrEnum):
    VF = "VF"
    VO = "VO"
    THREE_D = "3D"
    ICE = "ICE"


class ExtractResult(typing.TypedDict):
    cinema_attributes: list[boost_serializers.CinemaAttribut]
    showtimes: list[boost_serializers.ShowTime4]


class ShowStockData(typing.TypedDict):
    stock_uuid: str
    show_datetime: datetime.datetime
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
        Step 1: Fetch data from Boost API
        """
        try:
            cinema_attributes = self.api_client.get_cinemas_attributs()
            showtimes = self.api_client.get_showtimes()
        except Exception as exc:
            self._log(logging.WARNING, "Step 1 - Extract failed", {"exc": exc.__class__.__name__})
            raise

        return {
            "cinema_attributes": cinema_attributes,
            "showtimes": showtimes,
        }

    def _transform(self, extract_result: ExtractResult) -> list[LoadableData]:
        """
        Step 2:

        Make data easily loadable by :
            - grouping shows by movie
            - formatting shows and movie information
        """
        loadable_data_by_movie_uuid: dict[str, LoadableData] = {}

        ice_immersive_attribute_id = self._get_ice_immersive_attribute_id(extract_result["cinema_attributes"])

        for showtime in extract_result["showtimes"]:
            pass_culture_pricing = get_pcu_pricing_if_exists(showtime.showtimePricing)

            # we don't import the showtime if pass culture pricing is missing
            if not pass_culture_pricing:
                self._log(
                    logging.WARNING,
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

            movie_uuid = f"{showtime.film.id}%{self.venue_provider.venueId}%Boost"
            show_stock_data = self._transform_showtime_to_show_stock_data(
                showtime,
                movie_uuid,
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
            if cinema_attribute.title == "ICE Immersive":
                return cinema_attribute.id
        return None

    def _transform_showtime_to_show_stock_data(
        self,
        showtime: boost_serializers.ShowTime4,
        movie_uuid: str,
        pass_culture_pricing: boost_serializers.ShowtimePricing,
        ice_immersive_attribute_id: int | None,
    ) -> ShowStockData:
        features = []

        if ShowFeatures.VO == showtime.version["code"]:
            features.append(ShowFeatures.VO)
        elif ShowFeatures.VF == showtime.version["code"]:
            features.append(ShowFeatures.VF)

        if ShowFeatures.THREE_D == showtime.format["title"]:
            features.append(ShowFeatures.THREE_D)

        if ice_immersive_attribute_id is not None and ice_immersive_attribute_id in showtime.attributs:
            features.append(ShowFeatures.ICE)

        return {
            "stock_uuid": f"{movie_uuid}#{showtime.id}",
            "show_datetime": showtime.showDate,
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
            self._log(logging.WARNING, "Init - Provider inactive")
            raise exceptions.InactiveProvider()
        if not self.venue_provider.isActive:
            self._log(logging.WARNING, "Init - VenueProvider inactive")
            raise exceptions.InactiveVenueProvider()

        # Step 1 : Extract (API calls)
        result = self._extract()

        self._log(
            logging.DEBUG,
            "Step 1 - Extract done",
            {
                "cinema_attributes": [cinema_attribute.dict() for cinema_attribute in result["cinema_attributes"]],
                "showtimes": [showtime.dict() for showtime in result["showtimes"]],
            },
        )

        # Step 2 : Transform
        transform_result = self._transform(result)

        self._log(logging.DEBUG, " Step 2 - Transform done", transform_result)

    def _log(self, level: int, message: str, data: dict | list | None = None) -> None:
        """
        Prefix log message with class name & enrich extra dict with `venue_provider` information

        :level: level defined in logging package, either `logging.WARNING` or `logging.DEBUG`
        :data: dict to be added in extra dict under the "data" key
        """
        log_message = "[%s] %s" % (self.__class__.__name__, message)
        extra: dict = {
            "venue_id": self.venue_provider.venueId,
            "provider_id": self.venue_provider.providerId,
            "venue_provider_id": self.venue_provider.id,
            "venue_id_at_offer_provider": self.venue_provider.venueIdAtOfferProvider,
        }
        if data:
            extra["data"] = data

        if level == logging.WARNING:
            logger.warning(log_message, extra=extra)
        elif level == logging.DEBUG:
            logger.debug(log_message, extra=extra)
