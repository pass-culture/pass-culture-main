from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest.mock import call
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core import testing
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_existing_offers(self, client):
        # Given
        offer1 = offers_factories.OfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": True}
        response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        offer_1 = db.session.query(Offer).get(offer1.id)
        offer_2 = db.session.query(Offer).get(offer2.id)
        assert offer_1.isActive
        assert offer1.publicationDatetime
        assert offer1.publicationDatetime == offer1.bookingAllowedDatetime
        assert offer_2.isActive
        assert offer_2.publicationDatetime
        assert offer_2.publicationDatetime == offer_2.bookingAllowedDatetime

    def when_deactivating_existing_offers(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        finalization_datetime = datetime.now(timezone.utc)
        offer = offers_factories.OfferFactory(
            venue=venue,
            finalizationDatetime=finalization_datetime,
            publicationDatetime=finalization_datetime,
            bookingAllowedDatetime=finalization_datetime,
        )
        synchronized_offer = offers_factories.OfferFactory(
            lastProvider=providers_factories.ProviderFactory(), venue=venue
        )
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer.id, synchronized_offer.id], "isActive": False}
        with testing.assert_no_duplicated_queries():
            response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        first_offer = db.session.query(Offer).get(offer.id)
        assert first_offer.finalizationDatetime == finalization_datetime.replace(tzinfo=None)
        assert not first_offer.isActive
        assert not first_offer.publicationDatetime
        assert not first_offer.bookingAllowedDatetime
        assert not db.session.query(Offer).get(synchronized_offer.id).isActive

    def test_only_approved_offers_patch(self, client):
        approved_offer = offers_factories.OfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = client.with_session_auth("pro@example.com")
        data = {
            "ids": [approved_offer.id, pending_offer.id, rejected_offer.id],
            "isActive": True,
        }
        response = client.patch("/offers/active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert approved_offer.publicationDatetime
        assert not pending_offer.isActive
        assert not pending_offer.publicationDatetime
        assert not rejected_offer.isActive
        assert not rejected_offer.publicationDatetime

    def when_activating_synchronized_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue, isActive=False)

        provider = providers_factories.ProviderFactory()
        offer_that_should_stay_deactivated = offers_factories.OfferFactory(
            lastProvider=provider, venue=venue, isActive=False
        )
        providers_factories.VenueProviderFactory(provider=provider, venue=venue, isActive=False)

        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        response = client.patch(
            "/offers/active-status",
            json={"ids": [offer_that_should_stay_deactivated.id, offer.id], "isActive": True},
        )

        # Then
        assert response.status_code == 204
        assert not offer_that_should_stay_deactivated.isActive
        assert offer.isActive


@pytest.mark.usefixtures("db_session")
class ActivateFutureOffersTest:
    def test_activate_future_offers_and_notify_users_with_reminders(self, client):
        offer_to_publish_1 = offers_factories.OfferFactory(isActive=False)
        venue = offer_to_publish_1.venue
        offer_to_publish_2 = offers_factories.OfferFactory(isActive=False, venue=venue)
        offer_to_publish_3 = offers_factories.OfferFactory(isActive=False, venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        publication_date = datetime.utcnow() + timedelta(days=30)
        offers_factories.FutureOfferFactory(offer=offer_to_publish_1, publicationDate=publication_date)
        offers_factories.FutureOfferFactory(offer=offer_to_publish_2, publicationDate=publication_date)

        with patch(
            "pcapi.core.reminders.external.reminders_notifications.notify_users_future_offer_activated"
        ) as mock_notify_users_future_offer_activated:
            client = client.with_session_auth("pro@example.com")
            data = {"ids": [offer_to_publish_1.id, offer_to_publish_2.id], "isActive": True}
            response = client.patch("/offers/active-status", json=data)
            mock_notify_users_future_offer_activated.assert_has_calls(
                [call(offer_to_publish_1), call(offer_to_publish_2)], any_order=True
            )

        assert response.status_code == 204
        assert db.session.query(Offer).get(offer_to_publish_1.id).isActive
        assert db.session.query(Offer).get(offer_to_publish_2.id).isActive
        assert not db.session.query(Offer).get(offer_to_publish_3.id).isActive

    def test_deactivate_future_offers(self, client):
        offer_published_1 = offers_factories.OfferFactory()
        venue = offer_published_1.venue
        offer_published_2 = offers_factories.OfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        publication_date = datetime.utcnow() + timedelta(days=30)
        offers_factories.FutureOfferFactory(offer=offer_published_1, publicationDate=publication_date)
        offers_factories.FutureOfferFactory(offer=offer_published_2, publicationDate=publication_date)

        with patch(
            "pcapi.core.reminders.external.reminders_notifications.notify_users_future_offer_activated"
        ) as mock_notify_users_future_offer_activated:
            client = client.with_session_auth("pro@example.com")
            data = {"ids": [offer_published_1.id, offer_published_2.id], "isActive": False}
            response = client.patch("/offers/active-status", json=data)
            mock_notify_users_future_offer_activated.assert_not_called()

        assert response.status_code == 204
        assert not db.session.query(Offer).get(offer_published_1.id).isActive
        assert not db.session.query(Offer).get(offer_published_2.id).isActive
