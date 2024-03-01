import logging

from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import testing
from pcapi.utils import requests

from .base import BaseBackend


logger = logging.getLogger(__name__)

TESTING_ZENDESK_ID_OFFERER = "1111111"
TESTING_ZENDESK_ID_VENUE = "2222222"


class TestingBackend(BaseBackend):
    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        testing.zendesk_sell_requests.append({"action": "create", "type": type(offerer).__name__, "id": offerer.id})
        return {"id": TESTING_ZENDESK_ID_OFFERER}

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        testing.zendesk_sell_requests.append(
            {"action": "update", "type": type(offerer).__name__, "id": offerer.id, "zendesk_id": zendesk_id}
        )
        return {"id": zendesk_id}

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        testing.zendesk_sell_requests.append(
            {
                "action": "create",
                "type": type(venue).__name__,
                "id": venue.id,
                "parent_organization_id": parent_organization_id,
            }
        )
        return {"id": TESTING_ZENDESK_ID_VENUE}

    def update_venue(
        self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        testing.zendesk_sell_requests.append(
            {
                "action": "update",
                "type": type(venue).__name__,
                "id": venue.id,
                "zendesk_id": zendesk_id,
                "parent_organization_id": parent_organization_id,
            }
        )
        return {"id": zendesk_id}

    def search_contact(self, params: dict, session: requests.Session | None = None) -> dict:
        raise NotImplementedError()

    def get_offerer_by_id(self, offerer: offerers_models.Offerer) -> dict:
        return {"id": TESTING_ZENDESK_ID_OFFERER}

    def get_venue_by_id(self, venue: offerers_models.Venue) -> dict:
        return {"id": TESTING_ZENDESK_ID_VENUE}
