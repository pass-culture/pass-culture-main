from unittest.mock import patch

import pytest

from pcapi.core.educational import testing as educational_testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_patch_set_active_status(self, client):
        offer = CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer.id], "isActive": False}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch("/collective/offers/active-status", json=data)

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}
        assert offer.isActive is True

    def test_patch_set_inactive_status(self, client):
        offer = CollectiveOfferFactory(isActive=False)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer.id], "isActive": True}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch("/collective/offers/active-status", json=data)

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}
        assert offer.isActive is False
