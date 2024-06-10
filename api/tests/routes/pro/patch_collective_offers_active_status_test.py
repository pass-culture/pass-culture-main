from unittest.mock import patch

import pytest

from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.models import CollectiveOffer
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer1.id, offer2.id], "isActive": True}

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.with_session_auth("pro@example.com").patch("/collective/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOffer.query.get(offer1.id).isActive
        assert CollectiveOffer.query.get(offer2.id).isActive

    def when_deactivating_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": False}
        with testing.assert_no_duplicated_queries():
            response = client.patch("/collective/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not CollectiveOffer.query.get(offer1.id).isActive
        assert not CollectiveOffer.query.get(offer2.id).isActive


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_activating_all_existing_offers_active_status_when_cultural_partners_not_found(self, client):
        # Given
        offer1 = CollectiveOfferFactory(isActive=False)
        offer2 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": True}

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
            return_value=False,
        ):
            response = client.patch("/collective/offers/active-status", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"Partner": ["User not in Adage can't edit the offer"]}
        assert offer1.isActive is False


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_when_activating_all_existing_offers_active_status_with_1_offer_not_cancellable(self, client) -> None:
        # Given
        offer1 = CollectiveOfferFactory(isActive=False, validation=OfferValidationStatus.PENDING)
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(isActive=False, venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": True}

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.with_session_auth("pro@example.com").patch("/collective/offers/active-status", json=data)

        # Then
        assert response.status_code == 400
        assert "ids" in response.json.keys()
        assert len(response.json["ids"]) > 0
        assert "All orders must be cancellables." in response.json["ids"][0]
        assert offer1.isActive is False
        assert offer2.isActive is False
