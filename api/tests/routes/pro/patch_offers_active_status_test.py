import pytest

from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": True}
        response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert Offer.query.get(offer1.id).isActive
        assert Offer.query.get(offer2.id).isActive

    def when_deactivating_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory()
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        offers_update_queries = 3
        collective_offers_update_queries = 2  # collective + template

        # When
        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": False}
        with testing.assert_num_queries(
            testing.AUTHENTICATION_QUERIES + offers_update_queries + collective_offers_update_queries
        ):
            response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not Offer.query.get(offer1.id).isActive
        assert not Offer.query.get(offer2.id).isActive

    def test_only_approved_offers_patch(self, app):
        approved_offer = offers_factories.OfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {
            "ids": [humanize(approved_offer.id), humanize(pending_offer.id), humanize(rejected_offer.id)],
            "isActive": True,
        }
        response = client.patch("/offers/active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive

    def should_activate_collective_offers(self, client):
        # Given
        offer1 = offers_factories.EducationalEventOfferFactory(isActive=False, extraData={"isShowcase": False})
        venue = offer1.venue
        collective_offer = CollectiveOfferFactory(isActive=False, offerId=offer1.id, venue=venue)
        offer2 = offers_factories.EducationalEventOfferFactory(
            venue=venue, isActive=False, extraData={"isShowcase": True}
        )
        collective_offer_template = CollectiveOfferTemplateFactory(isActive=False, offerId=offer2.id, venue=venue)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": True}
        response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOffer.query.get(collective_offer.id).isActive
        assert CollectiveOfferTemplate.query.get(collective_offer_template.id).isActive

    def should_deactivate_collective_offers(self, client):
        # Given
        offer1 = offers_factories.EducationalEventOfferFactory(isActive=True, extraData={"isShowcase": False})
        venue = offer1.venue

        collective_offer = CollectiveOfferFactory(isActive=True, offerId=offer1.id, venue=venue)
        offer2 = offers_factories.EducationalEventOfferFactory(
            venue=venue, isActive=True, extraData={"isShowcase": True}
        )
        collective_offer_template = CollectiveOfferTemplateFactory(isActive=True, venue=venue, offerId=offer2.id)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": False}
        response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not CollectiveOffer.query.get(collective_offer.id).isActive
        assert not CollectiveOfferTemplate.query.get(collective_offer_template.id).isActive
