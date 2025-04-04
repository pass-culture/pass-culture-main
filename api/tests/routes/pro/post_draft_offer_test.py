import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.schemas import VenueTypeCode
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    def test_created_offer_should_be_inactive(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
            "extraData": {"gtl_id": "07000000"},
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
        assert response_dict["productId"] == None
        assert response_dict["extraData"] == {"gtl_id": "07000000"}
        assert response_dict["isDuo"] == False
        assert not offer.product

    def test_created_offer_should_return_url_if_set(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.LIVRE_NUMERIQUE.id,
            "url": "https://monsuperlivrenum.com/1345666",
            "venueId": venue.id,
            "extraData": {"gtl_id": "07000000"},
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 201
        assert response.json["url"] == "https://monsuperlivrenum.com/1345666"

    def test_created_offer_should_have_is_duo_set_to_true_if_subcategory_is_event_and_can_be_duo(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.CONFERENCE.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 201

        response_dict = response.json
        offer_id = response_dict["id"]
        offer = Offer.query.get(offer_id)
        assert response_dict["isDuo"] == True
        assert not offer.product

    @pytest.mark.features(WIP_EAN_CREATION=False)
    def test_create_offer_cd_without_product_venue_record_store_should_succeed(self, client):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.RECORD_STORE)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            "venueId": venue.id,
            "extraData": {"gtl_id": "07000000"},
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 201

    def test_created_offer_from_product_should_return_product_id(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean="9782123456803",
            # extraData=dict({"ean": "9782123456803"})
        )

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
            "productId": product.id,
            "extraData": {"ean": "9782123456803"},
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
        assert response_dict["productId"] == product.id
        # assert response_dict["extraData"] == {"ean": "9782123456803"}  # ne pas suppr a fix
        assert offer.ean == "9782123456803"
        assert offer.product == product
        assert offer._description is None
        assert offer.description == product.description

    def test_create_offer_other_than_cd_without_EAN_code_should_succeed_for_record_store(self, client):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.RECORD_STORE)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
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
        assert response_dict["productId"] is None
        assert offer.product is None

    def test_create_offer_cd_without_EAN_code_shoud_succeed_if_venue_is_not_record_store(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
            "venueId": venue.id,
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
        assert response_dict["productId"] is None
        assert offer.product is None

    def test_create_offer_record_store_cd_with_valid_ean_code(self, client):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.RECORD_STORE)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
            ean="1234567891234",
            # extraData=dict({"ean": "1234567891234"}),
        )

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
            "venueId": venue.id,
            "extraData": {"gtl_id": "07000000", "ean": "1234567891234"},
            "productId": product.id,
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
        assert response_dict["productId"] == offer.productId
        # assert response_dict["extraData"] == {"ean": "1234567891234"}  # ne pas suppr a fix
        assert offer.ean == "1234567891234"
        assert offer.product == product
        assert offer.description == product.description
        assert offer._description is None

    def test_create_offer_on_venue_with_accessibility_informations(self, client):
        venue = offerers_factories.VenueFactory(
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=False,
            visualDisabilityCompliant=False,
        )
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Ernestine",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 201

        offer = Offer.query.get(response.json["id"])
        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is False

    def test_create_offer_on_venue_with_no_accessibility_informations(self, client):
        venue = offerers_factories.VenueFactory(
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
        )
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

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

    def test_create_offer_on_venue_with_external_accessibility_provider_informations(self, client):
        venue = offerers_factories.VenueFactory(
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
        )
        offerers_factories.AccessibilityProviderFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Ernestine",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 201

        offer = Offer.query.get(response.json["id"])
        assert offer.audioDisabilityCompliant == True
        assert offer.mentalDisabilityCompliant == False
        assert offer.motorDisabilityCompliant == True
        assert offer.visualDisabilityCompliant == True


@pytest.mark.usefixtures("db_session")
class Returns400Test:

    @pytest.mark.parametrize(
        "partial_body,expected_status_code, expected_json",
        [
            # 400
            (
                {"name": "too long" * 30},
                400,
                {"name": ["Le titre de l’offre doit faire au maximum 90 caractères."]},
            ),
            (
                {"name": "Offre avec EAN dans le titre - 9782070286256"},
                400,
                {"name": ["Le titre d'une offre ne peut contenir l'EAN"]},
            ),
            (
                {"subcategoryId": "TOTO"},
                400,
                {"subcategory": ["La sous-catégorie de cette offre est inconnue"]},
            ),
            (
                {"url": "https:mince.e"},
                400,
                {"url": ['L\'URL doit commencer par "http://" ou "https://"']},
            ),
            (
                {
                    "url": "https://monlivrevirtuel.com/12345",
                    "subcategoryId": subcategories.LIVRE_PAPIER.id,
                },
                400,
                {"url": ['Une offre de sous-catégorie "Livre papier" ne peut contenir un champ `url`']},
            ),
            (
                {"subcategoryId": subcategories.LIVRE_NUMERIQUE.id},
                400,
                {"url": ['Une offre de catégorie "Livre numérique, e-book" doit contenir un champ `url`']},
            ),
            # 404
            (
                {"venueId": 1234642646},
                404,
                {},
            ),
        ],
    )
    def test_fail_when_json_body_has_incorrect_values(self, partial_body, expected_status_code, expected_json, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        json_body = {
            "name": "Le Visible et l'invisible - Suivi de notes de travail",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "venueId": venue.id,
        }
        json_body.update(**partial_body)
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=json_body)

        assert response.status_code == expected_status_code
        assert response.json == expected_json

    @pytest.mark.features(WIP_EAN_CREATION=True)
    def test_fail_if_venue_is_record_store_offer_is_cd_without_product(self, client):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.RECORD_STORE)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            "venueId": venue.id,
            "extraData": {"gtl_id": "07000000"},
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 400
        assert response.json["ean"] == ["EAN non reconnu. Assurez-vous qu'il n'y ait pas d'erreur de saisie."]

    @pytest.mark.features(WIP_EAN_CREATION=True)
    def test_fail_if_venue_is_record_store_offer_is_cd_with_unknown_product(self, client):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.RECORD_STORE)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "Celeste",
            "subcategoryId": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            "venueId": venue.id,
            "extraData": {"gtl_id": "07000000", "ean": "1234567891234"},
            "productId": 0,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 400
        assert response.json["ean"] == ["EAN non reconnu. Assurez-vous qu'il n'y ait pas d'erreur de saisie."]

    @pytest.mark.parametrize("subcategory_id", ["OEUVRE_ART", "BON_ACHAT_INSTRUMENT"])
    def test_fail_if_inactive_subcategory(self, client, subcategory_id):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {
            "name": "A cool offer name",
            "subcategoryId": subcategory_id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 400
        msg = "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        assert response.json["subcategory"] == [msg]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_user_is_not_attached_to_offerer(self, client):
        users_factories.ProFactory(email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory()

        data = {
            "name": "Les orphelins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "venueId": venue.id,
        }
        response = client.with_session_auth("user@example.com").post("/offers/draft", json=data)

        assert response.status_code == 403
        msg = "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        assert response.json["global"] == [msg]
