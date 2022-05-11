from datetime import datetime

import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_all_existing_offers(self, app):
        # Given
        offer1 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue, isActive=False)
        offer3 = CollectiveOfferTemplateFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": humanize(venue.id)}
        response = client.patch("/collective/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOffer.query.get(offer1.id).isActive
        assert CollectiveOffer.query.get(offer2.id).isActive
        assert CollectiveOfferTemplate.query.get(offer3.id).isActive

    def when_deactivating_all_existing_offers(self, app):
        # Given
        offer1 = CollectiveOfferFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue)
        offer3 = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"isActive": False}
        response = client.patch("/collective/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not CollectiveOffer.query.get(offer1.id).isActive
        assert not CollectiveOffer.query.get(offer2.id).isActive
        assert not CollectiveOfferTemplate.query.get(offer3.id).isActive

    def should_update_offers_by_given_filters(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        matching_offer1 = CollectiveOfferFactory(name="OKAY 1", venue=venue)
        CollectiveStockFactory(collectiveOffer=matching_offer1, beginningDatetime=datetime(2020, 10, 10, 12, 0, 0))
        matching_offer2 = CollectiveOfferFactory(name="OKAY 2", venue=venue)
        CollectiveStockFactory(collectiveOffer=matching_offer2, beginningDatetime=datetime(2020, 10, 10, 12, 0, 0))

        offer_out_of_date_range = CollectiveOfferFactory(name="OKAY 3", venue=venue)
        CollectiveStockFactory(
            collectiveOffer=offer_out_of_date_range,
            beginningDatetime=datetime(2020, 10, 12, 10, 0, 0),
        )
        offer_on_other_venue = CollectiveOfferFactory(name="OKAY 4")
        offer_with_not_matching_name = CollectiveOfferFactory(name="Pas celle-ci", venue=venue)

        data = {
            "isActive": False,
            "offererId": humanize(user_offerer.offerer.id),
            "venueId": humanize(venue.id),
            "name": "OKAY",
            "periodBeginningDate": "2020-10-09T00:00:00Z",
            "periodEndingDate": "2020-10-11T23:59:59Z",
        }
        client = TestClient(app.test_client()).with_session_auth(user_offerer.user.email)

        # When
        response = client.patch("/collective/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not CollectiveOffer.query.get(matching_offer1.id).isActive
        assert not CollectiveOffer.query.get(matching_offer2.id).isActive
        assert CollectiveOffer.query.get(offer_out_of_date_range.id).isActive
        assert CollectiveOffer.query.get(offer_on_other_venue.id).isActive
        assert CollectiveOffer.query.get(offer_with_not_matching_name.id).isActive

    def test_only_approved_offers_patch(self, app):
        approved_offer = CollectiveOfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": humanize(venue.id)}
        response = client.patch("/collective/offers/all-active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive
