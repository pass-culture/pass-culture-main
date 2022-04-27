from datetime import datetime

import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_all_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": humanize(venue.id)}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert Offer.query.get(offer1.id).isActive
        assert Offer.query.get(offer2.id).isActive

    def when_deactivating_all_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory()
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"isActive": False}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert not Offer.query.get(offer1.id).isActive
        assert not Offer.query.get(offer2.id).isActive

    def should_update_offers_by_given_filters(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        matching_offer1 = offers_factories.OfferFactory(name="OKAY 1", venue=venue)
        offers_factories.StockFactory(offer=matching_offer1, beginningDatetime=datetime(2020, 10, 10, 12, 0, 0))
        matching_offer2 = offers_factories.OfferFactory(name="OKAY 2", venue=venue)
        offers_factories.StockFactory(offer=matching_offer2, beginningDatetime=datetime(2020, 10, 10, 12, 0, 0))

        offer_out_of_date_range = offers_factories.OfferFactory(name="OKAY 3", venue=venue)
        offers_factories.StockFactory(
            offer=offer_out_of_date_range,
            beginningDatetime=datetime(2020, 10, 12, 10, 0, 0),
        )
        offer_on_other_venue = offers_factories.OfferFactory(name="OKAY 4")
        offer_with_not_matching_name = offers_factories.OfferFactory(name="Pas celle-ci", venue=venue)

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
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert not Offer.query.get(matching_offer1.id).isActive
        assert not Offer.query.get(matching_offer2.id).isActive
        assert Offer.query.get(offer_out_of_date_range.id).isActive
        assert Offer.query.get(offer_on_other_venue.id).isActive
        assert Offer.query.get(offer_with_not_matching_name.id).isActive

    def test_only_approved_offers_patch(self, app):
        approved_offer = offers_factories.OfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = TestClient(app.test_client()).with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": humanize(venue.id)}
        response = client.patch("/offers/all-active-status", json=data)

        assert response.status_code == 202
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive

    def should_activate_all_collective_offers(self, client):
        # Given
        offer1 = offers_factories.EducationalEventOfferFactory(isActive=False)
        venue = offer1.venue
        collective_offer = CollectiveOfferFactory(isActive=False, venue=venue, offerId=offer1.id)
        offer2 = offers_factories.EducationalEventOfferFactory(
            venue=venue, isActive=False, extraData={"isShowcase": True}
        )
        collective_offer_template = CollectiveOfferTemplateFactory(isActive=False, venue=venue, offerId=offer2.id)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": humanize(venue.id)}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert CollectiveOffer.query.get(collective_offer.id).isActive
        assert CollectiveOfferTemplate.query.get(collective_offer_template.id).isActive

    def should_deactivate_all_collective_offers(self, client):
        # Given
        offer1 = offers_factories.EducationalEventOfferFactory(isActive=True)
        venue = offer1.venue
        collective_offer = CollectiveOfferFactory(isActive=True, venue=venue, offerId=offer1.id)
        offer2 = offers_factories.EducationalEventOfferFactory(
            venue=venue, isActive=True, extraData={"isShowcase": True}
        )
        collective_offer_template = CollectiveOfferTemplateFactory(isActive=True, venue=venue, offerId=offer2.id)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"isActive": False, "page": 1, "venueId": humanize(venue.id)}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert not CollectiveOffer.query.get(collective_offer.id).isActive
        assert not CollectiveOfferTemplate.query.get(collective_offer_template.id).isActive

    def should_update_collective_offers_by_given_filters_and_not_collective_offer_templates_if_period_is_given(
        self, client
    ):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        matching_offer1 = offers_factories.EducationalEventOfferFactory(name="OKAY 1", venue=venue)
        matching_collective_offer = CollectiveOfferFactory(name="OKAY 1", venue=venue, offerId=matching_offer1.id)
        stock1 = offers_factories.StockFactory(
            offer=matching_offer1, beginningDatetime=datetime(2020, 10, 10, 12, 0, 0)
        )
        CollectiveStockFactory(
            collectiveOffer=matching_collective_offer,
            beginningDatetime=datetime(2020, 10, 10, 12, 0, 0),
            stockId=stock1.id,
        )
        matching_offer2 = offers_factories.EducationalEventOfferFactory(
            name="OKAY 2", venue=venue, extraData={"isShowcase": True}
        )
        matching_collective_offer_template = CollectiveOfferTemplateFactory(
            name="OKAY 2", venue=venue, offerId=matching_offer2.id
        )

        offer_out_of_date_range = offers_factories.EducationalEventOfferFactory(name="OKAY 3", venue=venue)
        collective_offer_out_of_date_range = CollectiveOfferFactory(
            name="OKAY 3", venue=venue, offerId=offer_out_of_date_range.id
        )
        stock2 = offers_factories.StockFactory(
            offer=offer_out_of_date_range,
            beginningDatetime=datetime(2020, 10, 12, 10, 0, 0),
        )
        CollectiveStockFactory(
            collectiveOffer=collective_offer_out_of_date_range,
            beginningDatetime=datetime(2020, 10, 12, 10, 0, 0),
            stockId=stock2.id,
        )
        offer_on_other_venue = offers_factories.EducationalEventOfferFactory(name="OKAY 4")
        collective_offer_on_other_venue = CollectiveOfferFactory(name="OKAY 4", offerId=offer_on_other_venue.id)
        offer_with_not_matching_name = offers_factories.EducationalEventOfferFactory(name="Pas celle-ci", venue=venue)
        collective_offer_with_not_matching_name = CollectiveOfferFactory(
            name="Pas celle-ci", venue=venue, offerId=offer_with_not_matching_name.id
        )

        data = {
            "isActive": False,
            "offererId": humanize(user_offerer.offerer.id),
            "venueId": humanize(venue.id),
            "name": "OKAY",
            "periodBeginningDate": "2020-10-09T00:00:00Z",
            "periodEndingDate": "2020-10-11T23:59:59Z",
        }
        client = client.with_session_auth(user_offerer.user.email)

        # When
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert not CollectiveOffer.query.get(matching_collective_offer.id).isActive
        assert CollectiveOfferTemplate.query.get(matching_collective_offer_template.id).isActive
        assert CollectiveOffer.query.get(collective_offer_out_of_date_range.id).isActive
        assert CollectiveOffer.query.get(collective_offer_on_other_venue.id).isActive
        assert CollectiveOffer.query.get(collective_offer_with_not_matching_name.id).isActive
