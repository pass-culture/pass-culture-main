from datetime import datetime

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import Offer
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200:
    def test_patch_offer(self, app):
        # Given
        offer = offers_factories.OfferFactory()
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        client = TestClient(app.test_client()).with_auth("user@example.com")
        data = {"name": "New name"}
        response = client.patch(f"/offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": humanize(offer.id),
        }
        assert Offer.query.get(offer.id).name == "New name"


@pytest.mark.usefixtures("db_session")
class Returns400:
    def when_trying_to_patch_forbidden_attributes(self, app):
        # Given
        offer = offers_factories.OfferFactory()
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "dateCreated": serialize(datetime(2019, 1, 1)),
            "dateModifiedAtLastProvider": serialize(datetime(2019, 1, 1)),
            "id": 1,
            "idAtProviders": 1,
            "lastProviderId": 1,
            "owningOffererId": "AA",
            "thumbCount": 2,
        }
        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.patch(f"offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["owningOffererId"] == ["Vous ne pouvez pas changer cette information"]
        forbidden_keys = {
            "dateCreated",
            "dateModifiedAtLastProvider",
            "id",
            "idAtProviders",
            "lastProviderId",
            "owningOffererId",
            "thumbCount",
        }
        for key in forbidden_keys:
            assert key in response.json

    def should_fail_when_url_is_not_properly_formatted(self, app):
        # Given
        virtual_venue = offers_factories.VirtualVenueFactory()
        offer = offers_factories.OfferFactory(venue=virtual_venue)
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "Les lièvres pas malins",
            "url": "missing.something",
        }
        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.patch(f"offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit commencer par "http://" ou "https://"']


@pytest.mark.usefixtures("db_session")
class Returns403:
    def when_user_is_not_attached_to_offerer(self, app):
        # Given
        offer = offers_factories.OfferFactory(name="Old name")
        offers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_auth("user@example.com")
        data = {"name": "New name"}
        response = client.patch(f"/offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert Offer.query.get(offer.id).name == "Old name"


class Returns404:
    def test_returns_404_if_offer_does_not_exist(self, app, db_session):
        # given
        user = users_factories.UserFactory()

        # when
        client = TestClient(app.test_client()).with_auth(email=user.email)
        response = client.patch("/offers/ADFGA", json={})

        # then
        assert response.status_code == 404
