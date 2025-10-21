import datetime
import decimal
import logging
import typing

from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.connectors.serialization import ems_serializers
from pcapi.core.providers import models
from pcapi.core.providers import repository
from pcapi.utils import date as date_utils

from .base_etl import BaseETLProcess
from .base_etl import ETLProcessException
from .base_etl import LoadableMovie
from .base_etl import ShowFeatures
from .base_etl import ShowStockData


logger = logging.getLogger(__name__)


class EMSExtractResult(typing.TypedDict):
    site_with_events: ems_serializers.SiteWithEvents


class EMSExtractTransformLoadProcess(BaseETLProcess[EMSScheduleConnector, EMSExtractResult]):
    """
    Integration to import products, offers, stocks & price_categories for a `Venue`
    linked to `EMS`.
    """

    def __init__(self, venue_provider: models.VenueProvider):
        """
        :venue_provider: must be linked to EMS provider
        """
        super().__init__(venue_provider=venue_provider, api_client=EMSScheduleConnector())
        assert venue_provider.venueIdAtOfferProvider  # to make mypy happy
        ems_cinema_details = repository.get_ems_cinema_details(venue_provider.venueIdAtOfferProvider)
        self.last_version = ems_cinema_details.lastVersion

    def _extract(self) -> EMSExtractResult:
        """
        Step 1: Fetch data from EMS API
        """
        schedules = self.api_client.get_schedules(self.last_version)

        site_with_events = None
        for site in schedules.sites:
            if site.id == self.venue_provider.venueIdAtOfferProvider:
                site_with_events = site
                break

        if not site_with_events:
            raise ETLProcessException("No data on API")

        return {"site_with_events": site_with_events}

    def _transform(self, extract_result: EMSExtractResult) -> list[LoadableMovie]:
        loadable_data_by_movie_uuid: dict[str, LoadableMovie] = {}
        for event in extract_result["site_with_events"].events:
            movie_uuid = f"{event.id}%{self.venue_provider.venueId}%EMS"
            movie_data = event.to_generic_movie()
            stocks_data: list[ShowStockData] = []

            for session in event.sessions:
                # datetime
                local_tz = date_utils.get_department_timezone(self.venue_provider.venue.departementCode)
                beginning_datetime = datetime.datetime.strptime(session.date, "%Y%m%d%H%M")
                beginning_datetime_no_tz = date_utils.local_datetime_to_default_timezone(
                    beginning_datetime, local_tz
                ).replace(tzinfo=None)
                # price
                price = decimal.Decimal(session.pass_culture_price)
                # features
                features = []
                if "vf" in session.features:
                    features.append(ShowFeatures.VF)
                elif "vo" in session.features:
                    features.append(ShowFeatures.VO)

                if "video_3d" in session.features:
                    features.append(ShowFeatures.THREE_D)

                stocks_data.append(
                    {
                        "features": features,
                        "price": price,
                        "price_label": f"Tarif pass Culture {price}€",
                        "remaining_quantity": None,
                        "show_datetime": beginning_datetime_no_tz,
                        "stock_uuid": f"{movie_uuid}#{session.id}",
                    }
                )

            if not stocks_data:  # we drop movies without shows
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

            loadable_data_by_movie_uuid[movie_uuid] = {
                "movie_uuid": movie_uuid,
                "movie_data": movie_data,
                "stocks_data": stocks_data,
            }

        return list(loadable_data_by_movie_uuid.values())

    def _extract_result_to_log_dict(self, extract_result: EMSExtractResult) -> dict:
        """Helper method to easily log result from extract step"""
        return {"site_with_events": extract_result["site_with_events"].dict()}
