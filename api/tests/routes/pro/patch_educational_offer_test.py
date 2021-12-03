from datetime import datetime

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_patch_educational_offer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
            subcategoryId="CINE_PLEIN_AIR",
        )
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "extraData": {"contactEmail": "toto@example.com"},
            "subcategoryId": "CONCERT",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": humanize(offer.id),
        }
        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.extraData == {"contactEmail": "toto@example.com", "contactPhone": "0600000000"}
        assert updated_offer.subcategoryId == "CONCERT"


class Returns400Test:
    def when_trying_to_patch_forbidden_attributes(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(isEducational=True)
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "dateCreated": serialize(datetime(2019, 1, 1)),
            "id": 1,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400
        assert response.json["dateCreated"] == ["Vous ne pouvez pas changer cette information"]
        forbidden_keys = {
            "dateCreated",
            "id",
        }
        for key in forbidden_keys:
            assert key in response.json

    def test_patch_non_approved_offer_fails(self, app, client):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, isEducational=True)
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_patch_offer_with_empty_name(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
        )
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": " "}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_null_name(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
        )
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": None}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400


class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(name="Old name", isEducational=True)
        offers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

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
        response = client.with_session_auth("user@example.com").patch("/offers/educational/ADFGA", json={})

        # then
        assert response.status_code == 404

    def test_returns_404_if_no_educational_offer_exist(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(isEducational=False)
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "extraData": {"contactEmail": "toto@example.com"},
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 404
        assert response.json == {
            "offerId": "no educational offer has been found with this id",
        }
