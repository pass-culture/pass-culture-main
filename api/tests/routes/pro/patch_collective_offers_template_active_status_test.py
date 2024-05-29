from unittest.mock import patch

import pytest

from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus


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

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            client = client.with_session_auth("pro@example.com")
            response = client.patch("/collective/offers-template/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOfferTemplate.query.filter_by(id=offer1.id).one().isActive
        assert CollectiveOfferTemplate.query.filter_by(id=offer2.id).one().isActive

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
        assert not CollectiveOfferTemplate.query.filter_by(id=offer1.id).one().isActive
        assert not CollectiveOfferTemplate.query.filter_by(id=offer2.id).one().isActive

    def test_only_approved_offers_patch(self, client):
        approved_offer = CollectiveOfferTemplateFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = CollectiveOfferTemplateFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = CollectiveOfferTemplateFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        data = {
            "ids": [approved_offer.id, pending_offer.id, rejected_offer.id],
            "isActive": True,
        }

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            client = client.with_session_auth("pro@example.com")
            response = client.patch("/collective/offers-template/active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_activating_all_existing_offers_active_status_when_cultural_partners_not_found(self, client):
        # Given
        offer1 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferTemplateFactory(venue=venue, isActive=False)

        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": True}

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
            return_value=False,
        ):
            response = client.patch("/collective/offers-template/active-status", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"Partner": ["User not in Adage can't edit the offer"]}
        assert offer1.isActive is False
