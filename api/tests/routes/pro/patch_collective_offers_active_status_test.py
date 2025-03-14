from unittest.mock import patch

import pytest

from pcapi.core import testing
from pcapi.core.educational import testing as educational_testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def when_activating_existing_offers(self, client):
        offer1 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [offer1.id, offer2.id], "isActive": True}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("pro@example.com").patch("/collective/offers/active-status", json=data)

        assert response.status_code == 204
        assert CollectiveOffer.query.get(offer1.id).isActive
        assert CollectiveOffer.query.get(offer2.id).isActive

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def when_deactivating_existing_offers(self, client):
        offer1 = CollectiveOfferFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": False}
        with testing.assert_no_duplicated_queries():
            response = client.patch("/collective/offers/active-status", json=data)

        assert response.status_code == 204
        assert not CollectiveOffer.query.get(offer1.id).isActive
        assert not CollectiveOffer.query.get(offer2.id).isActive

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_only_approved_offers_patch(self, client):
        approved_offer = CollectiveOfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        data = {
            "ids": [approved_offer.id, pending_offer.id, rejected_offer.id],
            "isActive": True,
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            client = client.with_session_auth("pro@example.com")
            response = client.patch("/collective/offers/active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
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

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, return_value=False):
            response = client.patch("/collective/offers/active-status", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"Partner": ["User not in Adage can't edit the offer"]}
        assert offer1.isActive is False

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_patch_active_status(self, client):
        offer = CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer.id], "isActive": False}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch("/collective/offers/active-status", json=data)

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}
        assert offer.isActive is True

        offer.isActive = False
        data = {"ids": [offer.id], "isActive": True}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch("/collective/offers/active-status", json=data)

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}
        assert offer.isActive is False
