import datetime
import decimal
import logging
import typing

from pcapi import settings
from pcapi.core.providers import models
from pcapi.core.providers.clients import cgr_serializers
from pcapi.core.providers.clients.cgr_client import CGRAPIClient
from pcapi.utils import date as date_utils

from .cinema_etl_template import CinemaETLProcessTemplate
from .cinema_etl_template import LoadableMovie
from .cinema_etl_template import ShowFeatures
from .cinema_etl_template import ShowStockData


logger = logging.getLogger(__name__)


class CGRExtractResult(typing.TypedDict):
    films: list[cgr_serializers.Film]


class CGRExtractTransformLoadProcess(CinemaETLProcessTemplate[CGRAPIClient, CGRExtractResult]):
    """
    Integration to import products, offers, stocks & price_categories for a `Venue`
    linked to `CGR`.
    """

    def __init__(self, venue_provider: models.VenueProvider):
        """
        :venue_provider: must be linked to CDS provider
        """
        assert venue_provider.venueIdAtOfferProvider  # to make mypy happy
        super().__init__(
            venue_provider=venue_provider,
            api_client=CGRAPIClient(
                cinema_id=venue_provider.venueIdAtOfferProvider,
                request_timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            ),
        )

    def _extract(self) -> CGRExtractResult:
        """
        Step 1: Fetch data from CGR API
        """
        return {"films": self.api_client.get_films()}

    def _transform(self, extract_result: CGRExtractResult) -> list[LoadableMovie]:
        loadable_data_by_movie_uuid: dict[str, LoadableMovie] = {}

        for film in extract_result["films"]:
            movie_uuid = f"{film.IDFilmAlloCine}%{self.venue_provider.venueId}%CGR"
            movie_data = film.to_generic_movie()
            stocks_data: list[ShowStockData] = []

            if not film.Seances:  # we drop movies without shows
                self._log(
                    logging.WARNING,
                    "Step 2 - Movie does not have shows",
                    {
                        "movie_uuid": movie_uuid,
                        "movie_title": movie_data.title,
                        "allocine_id": movie_data.allocine_id,
                        "visa": movie_data.visa,
                    },
                )
                continue

            for show in film.Seances:
                local_tz = date_utils.get_department_timezone(
                    self.venue_provider.venue.offererAddress.address.departmentCode
                )
                show_datetime = date_utils.local_datetime_to_default_timezone(
                    datetime.datetime.combine(show.Date, show.Heure), local_tz
                )
                show_datetime = show_datetime.astimezone(tz=datetime.timezone.utc).replace(tzinfo=None)

                features = [ShowFeatures.VF if show.Version == "VF" else ShowFeatures.VO]
                if show.Relief == "3D":
                    features.append(ShowFeatures.THREE_D)
                if show.bICE:
                    features.append(ShowFeatures.ICE)

                stocks_data.append(
                    {
                        "features": features,
                        "price": decimal.Decimal(str(show.PrixUnitaire)),
                        "price_label": show.libTarif,
                        "remaining_quantity": show.NbPlacesRestantes,
                        "show_datetime": show_datetime,
                        "stock_uuid": f"{movie_uuid}#{show.IDSeance}",
                    }
                )
            loadable_data_by_movie_uuid[movie_uuid] = {
                "movie_uuid": movie_uuid,
                "movie_data": movie_data,
                "stocks_data": stocks_data,
            }

        return list(loadable_data_by_movie_uuid.values())

    def _extract_result_to_log_dict(self, extract_result: CGRExtractResult) -> dict:
        """Helper method to easily log result from extract step"""
        return {"films": [film.model_dump_json() for film in extract_result["films"]]}
