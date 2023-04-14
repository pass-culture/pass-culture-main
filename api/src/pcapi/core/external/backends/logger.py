import logging

import requests

from pcapi.core.offerers import models as offerers_models

from .base import BaseBackend


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        logger.info("A request to Zendesk Sell API would be sent to create %s %d", type(offerer).__name__, offerer.id)
        return {"id": None}

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        logger.info("A request to Zendesk Sell API would be sent to update %s %d", type(offerer).__name__, offerer.id)
        return {"id": None}

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        logger.info("A request to Zendesk Sell API would be sent to create %s %d", type(venue).__name__, venue.id)
        return {"id": None}

    def update_venue(
        self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        logger.info("A request to Zendesk Sell API would be sent to update %s %d", type(venue).__name__, venue.id)
        return {"id": None}

    def search_contact(self, params: dict, session: requests.Session | None = None) -> dict:
        raise NotImplementedError()

    def get_offerer_by_id(self, offerer: offerers_models.Offerer) -> dict:
        return {"id": None}

    def get_venue_by_id(self, venue: offerers_models.Venue) -> dict:
        return {"id": None}
