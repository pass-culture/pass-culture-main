import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import GcuCompatibilityType
from pcapi.core.offers.models import ImageType
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_product_by_ean(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ProductFactory(
            description="Product description",
            name="Product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "ean": "1234567891011",
                "author": "Martin Dupont",
                "gtl_id": "02000000",
                "performer": "Martine Dupond",
            },
            gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE,
        )
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.RECTO)
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.VERSO)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select product join load mediations
        num_queries += 1  # select offerer join load venue
        num_queries += 1  # select offer
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get_product_by_ean/1234567891011/{offerer_id}")
            assert response.status_code == 200
        assert response.json == {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "subcategoryId": product.subcategoryId,
            "gtlId": product.extraData.get("gtl_id"),
            "author": product.extraData.get("author"),
            "performer": product.extraData.get("performer"),
            "images": product.images,
        }

    def test_get_product_by_ean_empty_product_description(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.ProductFactory(
            description=None,
            name="Product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": "1234567891011", "author": "Martin Dupont"},
            gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE,
        )

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select product join load mediations
        num_queries += 1  # select offerer join load venue
        num_queries += 1  # select offer
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get_product_by_ean/1234567891011/{offerer_id}")
            assert response.status_code == 200

    def test_get_product_by_ean_offerer_with_multiple_venues_offer_with_product(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        product = offers_factories.ProductFactory(
            description="Product description",
            name="Product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "ean": "1234567891011",
                "author": "Martin Dupont",
                "gtl_id": "02000000",
                "performer": "Martine Dupond",
            },
            gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE,
        )
        offers_factories.OfferFactory(product=product, venue=venue)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select product join load mediations
        num_queries += 1  # select offerer join load venue
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get_product_by_ean/1234567891011/{offerer_id}")
            assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class Returns422Test:
    def test_get_product_by_ean_not_gcu_compatible(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.ProductFactory(
            description="Product description",
            name="Product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": "EANDUPRODUIT", "author": "Martin Dupont"},
            gcuCompatibilityType=GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select product join load mediations
        num_queries += 1  # select offerer join load venue
        num_queries += 1  # select offer
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get_product_by_ean/EANDUPRODUIT/{offerer_id}")

            assert response.status_code == 422
            assert response.json == {"ean": ["EAN invalide. Ce produit n'est pas conforme à nos CGU."]}

    def test_product_does_not_exist(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select product join load mediations
        num_queries += 1  # select offerer join load venue
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get_product_by_ean/UNKNOWN/{offerer_id}")
            assert response.status_code == 422
            assert response.json == {"ean": ["EAN non reconnu. Assurez-vous qu'il n'y ait pas d'erreur de saisie."]}

    def test_get_product_by_ean_offer_already_exists_for_offerrer_with_only_one_venue(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        product = offers_factories.ProductFactory(
            description="Product description",
            name="Product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": "EANDUPRODUIT", "author": "Martin Dupont"},
            gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE,
        )
        offers_factories.OfferFactory(product=product, venue=venue)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select product join load mediations
        num_queries += 1  # select offerer join load venue
        num_queries += 1  # select offer
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get_product_by_ean/EANDUPRODUIT/{offerer_id}")

            assert response.status_code == 422
            assert response.json == {
                "ean": ["Une offre avec cet EAN existe déjà. Vous pouvez la retrouver dans l'onglet Offres."]
            }

    def test_offerer_does_not_exist(self, client):
        user = users_factories.UserFactory()
        offers_factories.ProductFactory(
            description="Product description",
            name="Product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": "EANDUPRODUIT", "author": "Martin Dupont"},
            gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE,
        )

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select product join load mediations
        num_queries += 1  # select offerer join load venue
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = test_client.get("/get_product_by_ean/EANDUPRODUIT/0")

            assert response.status_code == 422
            assert response.json == {"ean": ["Structure non reconnue."]}
