from unittest.mock import patch

import pytest

from pcapi.core import testing
from pcapi.core.educational import testing as educational_testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferTemplateFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferTemplateFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        data = {"ids": [offer1.id, offer2.id], "isActive": True}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            client = client.with_session_auth("pro@example.com")
            response = client.patch("/collective/offers-template/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert db.session.get(CollectiveOfferTemplate, offer1.id).isActive
        assert db.session.get(CollectiveOfferTemplate, offer2.id).isActive

    def when_deactivating_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferTemplateFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": False}
        with testing.assert_no_duplicated_queries():
            response = client.patch("/collective/offers-template/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not db.session.get(CollectiveOfferTemplate, offer1.id).isActive
        assert not db.session.get(CollectiveOfferTemplate, offer2.id).isActive


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_activating_all_existing_offers_active_status_when_cultural_partners_not_found(self, client):
        offer1 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferTemplateFactory(venue=venue, isActive=False)

        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": True}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, return_value=False):
            response = client.patch("/collective/offers-template/active-status", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"Partner": ["User not in Adage can't edit the offer"]}
        assert offer1.isActive is False

    def test_publish_offer_not_allowed_patch(self, client):
        approved_offer = CollectiveOfferTemplateFactory(isActive=True)
        venue = approved_offer.venue
        pending_offer = CollectiveOfferTemplateFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = CollectiveOfferTemplateFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        data = {
            "ids": [approved_offer.id, pending_offer.id, rejected_offer.id],
            "isActive": False,
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            client = client.with_session_auth("pro@example.com")
            response = client.patch("/collective/offers-template/active-status", json=data)

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}

        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive
