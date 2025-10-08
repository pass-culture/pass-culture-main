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


class ExtractResult(typing.TypedDict):
    price_category_labels: list[offers_models.PriceCategoryLabel]
    cinema_attributes: list[boost_serializers.CinemaAttribut]
    showtimes: list[boost_serializers.ShowTime4]


class TransformResult(typing.TypedDict):
    pass


class LoadableData(typing.TypedDict):
    product_data: dict
    stocks_data: list[dict]


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
            logger.warning(
                "[BoostETLProcess] Step 1 - Extract failed",
                extra={
                    "venue_id": self.venue_provider.venueId,
                    "provider_id": self.venue_provider.providerId,
                    "venue_provider_id": self.venue_provider.id,
                    "venue_id_at_offer_provider": self.venue_provider.venueIdAtOfferProvider,
                    "exc": exc.__class__.__name__,
                },
            )
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
        product_by_pass_uuid = {}

        for showtime in extract_result["showtimes"]:
            pass_culture_pricing = get_pcu_pricing_if_exists(showtime.showtimePricing)

            if not pass_culture_pricing:
                logger.warning(
                    "[BoostETLProcess] Step 2 - Missing pass Culture pricing",
                    extra={
                        "venue_id": self.venue_provider.venueId,
                        "provider_id": self.venue_provider.providerId,
                        "venue_provider_id": self.venue_provider.id,
                        "venue_id_at_offer_provider": self.venue_provider.venueIdAtOfferProvider,
                        "showtime_data": {
                            "id": showtime.id,
                            "date": showtime.showDate,
                            "film": {
                                "id": showtime.film.id,
                                "title": showtime.film.titleCnc,
                            },
                        },
                    },
                )
                continue

            movie_uuid = _build_movie_uuid(showtime.film.id, self.venue_provider.venue)

            if movie_uuid in product_by_pass_uuid:
                product_by_pass_uuid[movie_uuid]["showtimes"].append(showtime)
            else:
                product_by_pass_uuid[movie_uuid] = {"showtimes": [showtime], "product_data": showtime.film}
        return

    def execute(self) -> None:
        """
        Check provider & venue_provider are active, then execute the etl process (extract, transform, load)

        :raise: `InactiveProvider`, `InactiveVenueProvider`
        """
        # Check provider and venue_provider are active
        if not self.venue_provider.provider.isActive:
            raise exceptions.InactiveProvider()
        if not self.venue_provider.isActive:
            raise exceptions.InactiveVenueProvider()

        # Step 1 : Extract (API calls)
        result = self._extract()

        logger.debug(
            "[BoostETLProcess] Step 1 - Extract done",
            extra={
                "venue_id": self.venue_provider.venueId,
                "provider_id": self.venue_provider.providerId,
                "venue_provider_id": self.venue_provider.id,
                "venue_id_at_offer_provider": self.venue_provider.venueIdAtOfferProvider,
                "data": {
                    "cinema_attributes": [cinema_attribute.dict() for cinema_attribute in result["cinema_attributes"]],
                    "showtimes": [showtime.dict() for showtime in result["showtimes"]],
                    "price_category_labels": result["price_category_labels"],
                },
            },
        )


def _build_movie_uuid(film_id: int, venue: offerers_models.Venue) -> str:
    return f"{film_id}%{venue.id}%Boost"


def _build_stock_uuid(film_id: int, venue: offerers_models.Venue, showtime_id: int) -> str:
    return f"{_build_movie_uuid(film_id, venue)}#{showtime_id}"
