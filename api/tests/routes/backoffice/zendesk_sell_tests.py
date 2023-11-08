from flask import url_for
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import testing

from .helpers import html_parser
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class UpdateOffererOnZendeskSellTest(PostEndpointHelper):
    endpoint = "backoffice_web.zendesk_sell.update_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_sync_offerer_to_zendesk_sell(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)
        assert testing.zendesk_sell_requests == [{"action": "update", "type": "Offerer", "id": offerer.id}]
        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)


class UpdateVenueOnZendeskSellTest(PostEndpointHelper):
    endpoint = "backoffice_web.zendesk_sell.update_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_sync_permanent_venue_to_zendesk_sell(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

        assert testing.zendesk_sell_requests == [
            {"action": "update", "type": "Venue", "id": venue.id},
        ]

    def test_sync_virtual_venue_to_zendesk_sell(self, legit_user, authenticated_client):
        venue = offerers_factories.VirtualVenueFactory()
        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Ce lieu est virtuel ou non permanent"
        )

        assert not testing.zendesk_sell_requests
