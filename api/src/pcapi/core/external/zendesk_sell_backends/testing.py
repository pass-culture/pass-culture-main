import logging

import requests

from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import testing

from .base import BaseBackend


logger = logging.getLogger(__name__)


class TestingBackend(BaseBackend):
    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        testing.zendesk_sell_requests.append({"action": "create", "type": type(offerer).__name__, "id": offerer.id})
        return {"id": None}

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        testing.zendesk_sell_requests.append({"action": "update", "type": type(offerer).__name__, "id": offerer.id})
        return {"id": None}

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        testing.zendesk_sell_requests.append({"action": "create", "type": type(venue).__name__, "id": venue.id})
        return {"id": None}

    def update_venue(
        self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        testing.zendesk_sell_requests.append({"action": "update", "type": type(venue).__name__, "id": venue.id})
        return {"id": None}

    def search_contact(self, params: dict, session: requests.Session | None = None) -> dict:
        raise NotImplementedError()

    def get_offerer_by_id(self, offerer: offerers_models.Offerer) -> dict:
        return {"id": None}

    def get_venue_by_id(self, venue: offerers_models.Venue) -> dict:
        return {"id": None}
