import logging
import typing

from pcapi import settings
from pcapi.core.external_bookings.boost import serializers as boost_serializers
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.boost.client import get_pcu_pricing_if_exists
from pcapi.core.providers import models

from .base_etl import BaseETLProcess
from .base_etl import LoadableMovie
from .base_etl import ShowFeatures
from .base_etl import ShowStockData


logger = logging.getLogger(__name__)


class BoostExtractResult(typing.TypedDict):
    cinema_attributes: list[boost_serializers.CinemaAttribut]
    showtimes: list[boost_serializers.ShowTime4]


class BoostETLProcess(BaseETLProcess[BoostClientAPI, BoostExtractResult]):
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
        assert venue_provider.venueIdAtOfferProvider  # to make mypy happy
        super().__init__(
            venue_provider=venue_provider,
            api_client=BoostClientAPI(
                venue_provider.venueIdAtOfferProvider,
                request_timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            ),
        )

    def _extract(self) -> BoostExtractResult:
        """
        Step 1: Fetch data from Boost API
        """
        cinema_attributes = self.api_client.get_cinemas_attributs()
        showtimes = self.api_client.get_showtimes()

        return {
            "cinema_attributes": cinema_attributes,
            "showtimes": showtimes,
        }

    def _extract_result_to_log_dict(self, extract_result: BoostExtractResult) -> dict:
        """Helper method to easily log result from extract step"""
        return {
            "cinema_attributes": [cinema_attribute.dict() for cinema_attribute in extract_result["cinema_attributes"]],
            "showtimes": [showtime.dict() for showtime in extract_result["showtimes"]],
        }

    def _transform(self, extract_result: BoostExtractResult) -> list[LoadableMovie]:
        """
        Step 2: Transform Boost extract result into generic loadable movie data

        Make data easily loadable by :
            - grouping shows by movie
            - formatting shows and movie information
        """
        loadable_data_by_movie_uuid: dict[str, LoadableMovie] = {}

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
