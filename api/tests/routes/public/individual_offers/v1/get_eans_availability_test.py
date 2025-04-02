import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class GetEANsAvailabilityTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/products/ean/check_availability"
    endpoint_method = "get"

    expected_num_queries_success = 1  # 1. Select API key
    expected_num_queries_success += 1  # 3. Select products

    expected_num_queries_400 = 1  # 1. Select API key

    def test_should_return_eans_ordered_by_availability(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        # Valid EAN
        valid_ean = "1234567890123"
        offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            name="Vieux motard que jamais",
            ean=valid_ean,
            extraData={"subcategoryId": subcategories.LIVRE_PAPIER.id},
        )

        # Invalid EAN because of subcategory
        invalid_ean_because_not_in_allowed_subcategory = "2234567890123"
        offers_factories.ProductFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="Les 3000 mousquetaires contre Goldorak (collection Art & Essai)",
            ean=invalid_ean_because_not_in_allowed_subcategory,
            extraData={"subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id},
        )

        # Invalid EAN because not compliant with CGU
        invalid_ean_because_not_compliant_with_cgu = "3234567890123"
        offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
            name="Un livre un peu 'olé olé'",
            ean=invalid_ean_because_not_compliant_with_cgu,
            extraData={"subcategoryId": subcategories.LIVRE_PAPIER.id},
        )
        not_found_ean = "4234567890123"

        with testing.assert_num_queries(self.expected_num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url,
                params={
                    "eans": ",".join(
                        [
                            valid_ean,
                            invalid_ean_because_not_compliant_with_cgu,
                            invalid_ean_because_not_in_allowed_subcategory,
                            not_found_ean,
                        ]
                    )
                },
            )

        assert response.status_code == 200
        assert response.json == {
            "available": [valid_ean],
            "rejected": {
                "notCompliantWithCgu": [invalid_ean_because_not_compliant_with_cgu],
                "notFound": [not_found_ean],
                "subcategoryNotAllowed": [invalid_ean_because_not_in_allowed_subcategory],
            },
        }

        # With one EAN
        with testing.assert_num_queries(self.expected_num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url,
                params={"eans": valid_ean},
            )

        assert response.status_code == 200
        assert response.json == {
            "available": [valid_ean],
            "rejected": {
                "notCompliantWithCgu": [],
                "notFound": [],
                "subcategoryNotAllowed": [],
            },
        }

        # With duplicate EAN
        with testing.assert_num_queries(self.expected_num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url,
                params={
                    "eans": ",".join(
                        [
                            invalid_ean_because_not_compliant_with_cgu,
                            invalid_ean_because_not_compliant_with_cgu,
                            invalid_ean_because_not_in_allowed_subcategory,
                        ]
                    )
                },
            )

        assert response.status_code == 200
        assert response.json == {
            "available": [],
            "rejected": {
                "notCompliantWithCgu": [invalid_ean_because_not_compliant_with_cgu],
                "notFound": [],
                "subcategoryNotAllowed": [invalid_ean_because_not_in_allowed_subcategory],
            },
        }

    @pytest.mark.parametrize(
        "eans_list,expected_msg",
        [
            ([], "EAN list must not be empty"),
            (["1234567890123" for _ in range(101)], "Too many EANs"),
            (["1234567890123", "coucou"], "EAN must be an integer"),
            (["1234567890123", "11111"], "Only 13 characters EAN are accepted"),
        ],
    )
    def test_should_raise_400_because_eans_query_param_is_invalid(self, client: TestClient, eans_list, expected_msg):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.expected_num_queries_400):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url,
                params={"eans": ",".join(eans_list)},
            )
            assert response.status_code == 400
            assert response.json == {"eans": [expected_msg]}
