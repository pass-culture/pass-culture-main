import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import Offer
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    def test_created_offer_should_be_inactive(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
            "extraData": {"ean": "9782123456803", "gtl_id": "07000000"},
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 201

        response_dict = response.json
        offer_id = response_dict["id"]
        offer = Offer.query.get(offer_id)
        assert offer.isActive is False
        assert response_dict["venue"]["id"] == offer.venue.id
        assert response_dict["name"] == "Celeste"
        assert response_dict["id"] == offer.id
        assert response_dict["extraData"] == {"ean": "9782123456803", "gtl_id": "07000000"}
        assert not offer.product

    def test_create_offer_on_venue_with_accessibility_informations(self, client):
        # Given
        venue = offerers_factories.VenueFactory(
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=False,
            visualDisabilityCompliant=True,
        )
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "name": "Ernestine",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)
        assert response.status_code == 201

        offer = Offer.query.get(response.json["id"])
        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is False
        assert offer.motorDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is True

    def test_create_offer_on_venue_with_no_accessibility_informations(self, client):
        # Given
        venue = offerers_factories.VenueFactory(
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
        )
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "name": "Ernestine",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)
        assert response.status_code == 201

        offer = Offer.query.get(response.json["id"])
        assert offer.audioDisabilityCompliant is None
        assert offer.mentalDisabilityCompliant is None
        assert offer.motorDisabilityCompliant is None
        assert offer.visualDisabilityCompliant is None


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_fail_if_venue_is_not_found(self, client):
        # Given
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": 1,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        # Then
        assert response.status_code == 404

    def test_fail_if_name_too_long(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "name": "too long" * 30,
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["name"] == ["Le titre de l’offre doit faire au maximum 90 caractères."]

    def test_fail_if_unknown_subcategory(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "name": "Name",
            "subcategoryId": "TOTO",
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    @pytest.mark.parametrize("subcategory_id", ["OEUVRE_ART", "BON_ACHAT_INSTRUMENT"])
    def test_fail_if_inactive_subcategory(self, client, subcategory_id):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "name": "A cool offer name",
            "subcategoryId": subcategory_id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        # Then
        assert response.status_code == 400
        msg = "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        assert response.json["subcategory"] == [msg]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_user_is_not_attached_to_offerer(self, client):
        # Given
        users_factories.ProFactory(email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory()

        # When
        data = {
            "name": "Les orphelins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        # Then
        assert response.status_code == 403
        msg = "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        assert response.json["global"] == [msg]
