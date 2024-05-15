from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_all_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue, isActive=False)
        offer3 = CollectiveOfferTemplateFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": venue.id}
        with patch("pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"):
            response = client.patch("/collective/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOffer.query.get(offer1.id).isActive
        assert CollectiveOffer.query.get(offer2.id).isActive
        assert CollectiveOfferTemplate.query.get(offer3.id).isActive

    def when_deactivating_all_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue)
        offer3 = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"isActive": False}
        with patch("pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"):
            response = client.patch("/collective/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not CollectiveOffer.query.get(offer1.id).isActive
        assert not CollectiveOffer.query.get(offer2.id).isActive
        assert not CollectiveOfferTemplate.query.get(offer3.id).isActive

    def should_update_offers_by_given_filters(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        matching_offer1 = CollectiveOfferFactory(name="OKAY 1", venue=venue)
        CollectiveStockFactory(
            collectiveOffer=matching_offer1,
            startDatetime=datetime(2020, 10, 10, 12, 0, 0),
            endDatetime=datetime(2020, 10, 10, 12, 0, 0),
        )
        matching_offer2 = CollectiveOfferFactory(name="OKAY 2", venue=venue)
        CollectiveStockFactory(
            collectiveOffer=matching_offer2,
            startDatetime=datetime(2020, 10, 10, 12, 0, 0),
            endDatetime=datetime(2020, 10, 10, 12, 0, 0),
        )

        offer_out_of_date_range = CollectiveOfferFactory(name="OKAY 3", venue=venue)
        CollectiveStockFactory(
            collectiveOffer=offer_out_of_date_range,
            startDatetime=datetime(2020, 10, 12, 10, 0, 0),
            endDatetime=datetime(2020, 10, 12, 10, 0, 0),
        )
        offer_on_other_venue = CollectiveOfferFactory(name="OKAY 4")
        offer_with_not_matching_name = CollectiveOfferFactory(name="Pas celle-ci", venue=venue)

        data = {
            "isActive": False,
            "offererId": user_offerer.offerer.id,
            "venueId": venue.id,
            "name": "OKAY",
            "periodBeginningDate": "2020-10-09T00:00:00Z",
            "periodEndingDate": "2020-10-11T23:59:59Z",
        }
        client = client.with_session_auth(user_offerer.user.email)

        # When
        with patch("pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"):
            response = client.patch("/collective/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not CollectiveOffer.query.get(matching_offer1.id).isActive
        assert not CollectiveOffer.query.get(matching_offer2.id).isActive
        assert CollectiveOffer.query.get(offer_out_of_date_range.id).isActive
        assert CollectiveOffer.query.get(offer_on_other_venue.id).isActive
        assert CollectiveOffer.query.get(offer_with_not_matching_name.id).isActive

    def test_only_approved_offers_patch(self, client):
        approved_offer = CollectiveOfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = client.with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": venue.id}
        with patch("pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"):
            response = client.patch("/collective/offers/all-active-status", json=data)

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
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {
            "isActive": True,
            "offererId": offerer.id,
            "page": 1,
            "venueId": venue.id,
        }

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
            return_value=False,
        ):
            response = client.patch("/collective/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"Partner": ["User not in Adage can't edit the offer"]}
        assert offer1.isActive is False
