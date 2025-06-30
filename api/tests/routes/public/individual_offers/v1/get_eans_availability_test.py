import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


valid_ean = "1234567890123"
ean_not_in_allowed_subcategory = "2234567890123"
ean_not_compliant_with_cgu = "3234567890123"
not_found_ean = "4234567890123"


@pytest.mark.usefixtures("db_session")
class GetEANsAvailabilityTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/products/ean/check_availability"
    endpoint_method = "get"

    expected_num_queries_success = 1  # 1. Select API key
    expected_num_queries_success += 1  # 3. Select products

    expected_num_queries_400 = 1  # 1. Select API key
    expected_num_queries_400 += 1  # rollback atomic

    @pytest.mark.parametrize(
        "eans,expected_response_json",
        [
            (
                [valid_ean, ean_not_compliant_with_cgu, ean_not_in_allowed_subcategory, not_found_ean],
                {
                    "available": [valid_ean],
                    "rejected": {
                        "notCompliantWithCgu": [ean_not_compliant_with_cgu],
                        "notFound": [not_found_ean],
                        "subcategoryNotAllowed": [ean_not_in_allowed_subcategory],
                    },
                },
            ),
            (  # With one EAN
                [valid_ean],
                {
                    "available": [valid_ean],
                    "rejected": {
                        "notCompliantWithCgu": [],
                        "notFound": [],
                        "subcategoryNotAllowed": [],
                    },
                },
            ),
            (  # With duplicate EAN
                [ean_not_compliant_with_cgu, ean_not_compliant_with_cgu, ean_not_in_allowed_subcategory],
                {
                    "available": [],
                    "rejected": {
                        "notCompliantWithCgu": [ean_not_compliant_with_cgu],
                        "notFound": [],
                        "subcategoryNotAllowed": [ean_not_in_allowed_subcategory],
                    },
                },
            ),
        ],
    )
    def test_should_return_eans_ordered_by_availability(self, eans, expected_response_json):
        plain_api_key, _ = self.setup_provider()
        # Valid EAN
        offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            name="Vieux motard que jamais",
            ean=valid_ean,
            extraData={"subcategoryId": subcategories.LIVRE_PAPIER.id},
        )
        # Invalid EAN because of subcategory
        offers_factories.ProductFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="Les 3000 mousquetaires contre Goldorak (collection Art & Essai)",
            ean=ean_not_in_allowed_subcategory,
            extraData={"subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id},
        )
        # Invalid EAN because not compliant with CGU
        offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            gcuCompatibilityType=offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
            name="Un livre un peu 'olé olé'",
            ean=ean_not_compliant_with_cgu,
            extraData={"subcategoryId": subcategories.LIVRE_PAPIER.id},
        )

        with testing.assert_num_queries(self.expected_num_queries_success):
            response = self.make_request(plain_api_key, query_params={"eans": ",".join(eans)})

        assert response.status_code == 200
        assert response.json == expected_response_json

    @pytest.mark.parametrize(
        "eans_list,expected_msg",
        [
            ([], "EAN list must not be empty"),
            (["1234567890123" for _ in range(101)], "Too many EANs"),
            (["1234567890123", "coucou"], "EAN must be an integer"),
            (["1234567890123", "11111"], "Only 13 characters EAN are accepted"),
        ],
    )
    def test_should_raise_400_because_eans_query_param_is_invalid(self, eans_list, expected_msg):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.expected_num_queries_400):
            response = self.make_request(plain_api_key, query_params={"eans": ",".join(eans_list)})
            assert response.status_code == 400
            assert response.json == {"eans": [expected_msg]}
