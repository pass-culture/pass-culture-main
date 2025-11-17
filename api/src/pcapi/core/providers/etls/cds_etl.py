import decimal
import logging
import typing

from pcapi import settings
from pcapi.core.providers import models
from pcapi.core.providers import repository
from pcapi.core.providers.clients import cds_serializers
from pcapi.core.providers.clients.cds_client import CineDigitalServiceAPIClient
from pcapi.utils import date as date_utils

from .cinema_etl_template import CinemaETLProcessTemplate
from .cinema_etl_template import LoadableMovie
from .cinema_etl_template import ShowFeatures
from .cinema_etl_template import ShowStockData


logger = logging.getLogger(__name__)


class CineDigitalServiceExtractResult(typing.TypedDict):
    movies: list[cds_serializers.MediaCDS]
    media_options: dict[int, str]
    shows: list[cds_serializers.ShowCDS]
    voucher_types: list[cds_serializers.VoucherTypeCDS]
    is_internet_sale_gauge_active: bool


class CDSExtractTransformLoadProcess(
    CinemaETLProcessTemplate[CineDigitalServiceAPIClient, CineDigitalServiceExtractResult]
):
    """
    Integration to import products, offers, stocks & price_categories for a `Venue`
    linked to `CDS`.
    """

    def __init__(self, venue_provider: models.VenueProvider):
        """
        :venue_provider: must be linked to CDS provider
        """
        assert venue_provider.venueIdAtOfferProvider  # to make mypy happy
        cinema_details = repository.get_cds_cinema_details(venue_provider.venueIdAtOfferProvider)
        super().__init__(
            venue_provider=venue_provider,
            api_client=CineDigitalServiceAPIClient(
                cinema_id=venue_provider.venueIdAtOfferProvider,
                account_id=cinema_details.accountId,
                cinema_api_token=cinema_details.cinemaApiToken,
                request_timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            ),
        )

    def _extract(self) -> CineDigitalServiceExtractResult:
        """
        Step 1: Fetch data from CDS API
        """
        return {
            "movies": self.api_client.get_venue_movies(),
            "media_options": self.api_client.get_media_options(),
            "shows": self.api_client.get_shows(),
            "voucher_types": self.api_client.get_pc_voucher_types(),
            "is_internet_sale_gauge_active": self.api_client.get_internet_sale_gauge_active(),
        }

    def _transform(self, extract_result: CineDigitalServiceExtractResult) -> list[LoadableMovie]:
        loadable_data_by_movie_uuid: dict[str, LoadableMovie] = {}
        is_internet_sale_gauge_active = extract_result["is_internet_sale_gauge_active"]
        for movie in extract_result["movies"]:
            movie_uuid = f"{movie.id}%{self.venue_provider.venueId}%CDS"
            loadable_data_by_movie_uuid[movie_uuid] = {
                "movie_data": movie.to_generic_movie(),
                "movie_uuid": movie_uuid,
                "stocks_data": [],
            }

        for show in extract_result["shows"]:
            show_movie_uuid = f"{show.media.id}%{self.venue_provider.venueId}%CDS"
            if show_movie_uuid not in loadable_data_by_movie_uuid:
                self._log(
                    logging.WARNING,
                    "Step 2 - Missing movie",
                    {"show_id": show.id, "show_datetime": show.showtime},
                )
                continue

            # not an actual call to CDS API
            # see TODO above the method `get_voucher_type_for_show`
            voucher_type = self.api_client.get_voucher_type_for_show(show, extract_result["voucher_types"])
            if not voucher_type:
                self._log(
                    logging.WARNING,
                    "Step 2 - Missing pass Culture tariff",
                    {"show_id": show.id, "show_datetime": show.showtime},
                )
                continue
            assert voucher_type.tariff  # to make mypy happy

            show_media_options = []

            for option in show.shows_mediaoptions_collection:
                if option.media_options_id.id in extract_result["media_options"]:
                    show_media_options.append(extract_result["media_options"][option.media_options_id.id])

            features = []

            if ShowFeatures.VO in show_media_options:
                features.append(ShowFeatures.VO)
            elif ShowFeatures.VF in show_media_options:
                features.append(ShowFeatures.VF)

            if ShowFeatures.THREE_D in show_media_options:
                features.append(ShowFeatures.THREE_D)

            remaining_quantity = show.remaining_place
            if is_internet_sale_gauge_active:
                remaining_quantity = show.internet_remaining_place

            local_tz = date_utils.get_department_timezone(
                self.venue_provider.venue.offererAddress.address.departmentCode
            )
            naive_utc_show_datetime = date_utils.local_datetime_to_default_timezone(show.showtime, local_tz).replace(
                tzinfo=None
            )

            stock_data: ShowStockData = {
                "features": features,
                "price": decimal.Decimal(str(voucher_type.tariff.price)),
                "price_label": voucher_type.tariff.label,
                "remaining_quantity": remaining_quantity,
                "show_datetime": naive_utc_show_datetime,
                "stock_uuid": f"{show_movie_uuid}#{show.id}",
            }
            loadable_data_by_movie_uuid[show_movie_uuid]["stocks_data"].append(stock_data)

        loadable_movies = []

        for loadable_movie in loadable_data_by_movie_uuid.values():
            if not loadable_movie["stocks_data"]:  # we drop movies without shows
                self._log(
                    logging.WARNING,
                    "Step 2 - Movie does not have shows",
                    {
                        "movie_uuid": loadable_movie["movie_uuid"],
                        "movie_title": loadable_movie["movie_data"].title,
                        "allocine_id": loadable_movie["movie_data"].allocine_id,
                        "visa": loadable_movie["movie_data"].visa,
                    },
                )
                continue
            loadable_movies.append(loadable_movie)

        return loadable_movies

    def _extract_result_to_log_dict(self, extract_result: CineDigitalServiceExtractResult) -> dict:
        """Helper method to easily log result from extract step"""
        return {
            "movies": [movie.model_dump_json() for movie in extract_result["movies"]],
            "media_options": extract_result["media_options"],
            "shows": [show.model_dump_json() for show in extract_result["shows"]],
        }
