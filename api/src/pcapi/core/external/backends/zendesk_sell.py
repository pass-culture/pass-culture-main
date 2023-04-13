import logging

import requests

from pcapi import settings
from pcapi.core.external.backends.base import BaseBackend
from pcapi.core.offerers import models as offerers_models


logger = logging.getLogger(__name__)


ZENDESK_SELL_API_KEY = settings.ZENDESK_SELL_API_KEY
ZENDESK_SELL_API_URL = settings.ZENDESK_SELL_API_URL


class ZendeskSellBackend(BaseBackend):
    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        response = {}
        data = self._get_offerer_data(offerer, created)
        try:
            response = self._query_api("POST", "/v2/contacts", data, None)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while creating offerer on Zendesk Sell", extra={"venue_id": offerer.id, "error": err})
        return response

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
        response = {}
        data = self._get_offerer_data(offerer)
        try:
            response = self._query_api("PUT", f"/v2/contacts/{zendesk_id}", data, None)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while updating offerer on Zendesk Sell", extra={"venue_id": offerer.id, "error": err})
        return response

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        response = {}
        data = self._get_venue_data(venue, parent_organization_id, created)
        try:
            response = self._query_api("POST", "/v2/contacts", data, None)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while creating venue on Zendesk Sell", extra={"venue_id": venue.id, "error": err})
        return response

    def update_venue(self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
        response = {}
        data = self._get_venue_data(venue, parent_organization_id)
        try:
            response = self._query_api("PUT", f"/v2/contacts/{zendesk_id}", data, None)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while udpating venue on Zendesk Sell", extra={"venue_id": venue.id, "error": err})
        return response
