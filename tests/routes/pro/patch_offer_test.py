from datetime import datetime

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories
from pcapi.models import Offer
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_patch_offer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory()
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "externalTicketOfficeUrl": "http://example.net",
            "mentalDisabilityCompliant": True,
        }
        response = client.with_auth("user@example.com").patch(f"/offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": humanize(offer.id),
        }
        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.externalTicketOfficeUrl == "http://example.net"
        assert updated_offer.mentalDisabilityCompliant


class Returns400Test:
    def when_trying_to_patch_forbidden_attributes(self, app, client):
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
            "subcategoryId": subcategories.LIVRE_PAPIER,
            "type": subcategories.LIVRE_PAPIER.matching_type,
        }
        response = client.with_auth("user@example.com").patch(f"offers/{humanize(offer.id)}", json=data)

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
            "subcategoryId",
            "type",
        }
        for key in forbidden_keys:
            assert key in response.json

    def should_fail_when_url_has_no_scheme(self, app, client):
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
        response = client.with_auth("user@example.com").patch(f"offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_externalTicketOfficeUrl_has_no_scheme(self, app, client):
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
            "externalTicketOfficeUrl": "missing.something",
        }
        response = client.with_auth("user@example.com").patch(f"offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_url_has_no_host(self, app, client):
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
            "url": "https://missing",
        }
        response = client.with_auth("user@example.com").patch(f"offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def should_fail_when_externalTicketOfficeUrl_has_no_host(self, app, client):
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
            "externalTicketOfficeUrl": "https://missing",
        }
        response = client.with_auth("user@example.com").patch(f"offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def test_patch_non_approved_offer_fails(self, app, client):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        response = client.with_auth("user@example.com").patch(f"/offers/{humanize(offer.id)}", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]


class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(name="Old name")
        offers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_auth("user@example.com").patch(f"/offers/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert Offer.query.get(offer.id).name == "Old name"


class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, app, client):
        # given
        users_factories.UserFactory(email="user@example.com")

        # when
        response = client.with_auth("user@example.com").patch("/offers/ADFGA", json={})

        # then
        assert response.status_code == 404
