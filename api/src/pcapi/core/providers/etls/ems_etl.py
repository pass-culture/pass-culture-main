import logging
import typing

from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.connectors.serialization import ems_serializers
from pcapi.core.providers import models
from pcapi.core.providers import repository

from .base_etl import BaseETLProcess
from .base_etl import ETLProcessException
from .base_etl import LoadableMovie


logger = logging.getLogger(__name__)


class EMSExtractResult(typing.TypedDict):
    site_with_events: ems_serializers.SiteWithEvents


class EMSETLProcess(BaseETLProcess[EMSScheduleConnector, EMSExtractResult]):
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
        return list(loadable_data_by_movie_uuid.values())

    def _extract_result_to_log_dict(self, extract_result: EMSExtractResult) -> dict:
        """Helper method to easily log result from extract step"""
        return {"site_with_events": extract_result["site_with_events"].dict()}
