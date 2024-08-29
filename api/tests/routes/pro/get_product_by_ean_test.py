import pytest

from pcapi.core.categories import subcategories_v2
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import GcuCompatibilityType
from pcapi.core.offers.models import TiteliveImageType
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # Session
    # User
    # Product
    # productMediations (joined query)
    number_of_queries = 4

    def test_get_product_by_ean(self, client):
        # Given
        user = users_factories.UserFactory()
        product = offers_factories.ProductFactory(
            description="Product description",
            name="Product name",
            subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
            extraData={
                "ean": "1234567891011",
                "author": "Martin Dupont",
                "gtl_id": "02000000",
                "performer": "Martine Dupond",
            },
            gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE,
        )
        offers_factories.ProductMediationFactory(
            product=product, url="https://url.com", imageType=TiteliveImageType.RECTO
        )
        offers_factories.ProductMediationFactory(
            product=product, url="https://url.com/verso", imageType=TiteliveImageType.VERSO
        )

        # When
        test_client = client.with_session_auth(email=user.email)
        with assert_num_queries(self.number_of_queries):
            response = test_client.get(f"/get_product_by_ean/{product.extraData.get('ean')}")

            # Then
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


@pytest.mark.usefixtures("db_session")
class Returns422Test:
    # Session
    # User
    # Product
    number_of_queries = 3

    def test_get_product_by_ean_not_gcu_compatible(self, client):
        # Given
        user = users_factories.UserFactory()
        product = offers_factories.ProductFactory(
            description="Product description",
            name="Product name",
            subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
            extraData={"ean": "EANDUPRODUIT", "author": "Martin Dupont"},
            gcuCompatibilityType=GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        # When
        test_client = client.with_session_auth(email=user.email)
        # One more query to get the product mediations as one product is found but not compatible
        with assert_num_queries(self.number_of_queries + 1):
            response = test_client.get(f"/get_product_by_ean/{product.extraData.get('ean')}")

            # Then
            assert response.status_code == 422
            assert response.json == {"ean": ["EAN invalide. Ce produit n'est pas conforme à nos CGU."]}

    def test_product_does_not_exist(self, client):
        user = users_factories.UserFactory()

        test_client = client.with_session_auth(email=user.email)
        with assert_num_queries(self.number_of_queries):
            response = test_client.get("/get_product_by_ean/UNKNOWN")

            assert response.status_code == 422
            assert response.json == {"ean": ["EAN non reconnu. Assurez-vous qu'il n'y ait pas d'erreur de saisie."]}
