import pytest

from pcapi.core import testing
from pcapi.core.educational import factories as educational_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalInstitutionTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/educational-institutions/"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select educational_institution

    def test_list_educational_institutions(self):
        plain_api_key, _ = self.setup_provider()
        expected_json = []
        for _ in range(0, 6):
            educational_institution = educational_factories.EducationalInstitutionFactory()
            expected_json.append(
                {
                    "id": educational_institution.id,
                    "uai": educational_institution.institutionId,
                    "name": educational_institution.name,
                    "postalCode": educational_institution.postalCode,
                    "city": educational_institution.city,
                    "institutionType": educational_institution.institutionType,
                }
            )

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert response.json == expected_json

    @pytest.mark.parametrize("postal_code_param", ["44100", "41"])
    def test_search_educational_institutions_postal_code(self, postal_code_param):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(postalCode="44100")
        educational_factories.EducationalInstitutionFactory()

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, query_params={"postalCode": postal_code_param})
            assert response.status_code == 200

        assert response.json == [
            {
                "id": educational_institution1.id,
                "uai": educational_institution1.institutionId,
                "name": educational_institution1.name,
                "postalCode": educational_institution1.postalCode,
                "city": educational_institution1.city,
                "institutionType": educational_institution1.institutionType,
            },
        ]

    def test_search_educational_institutions_id(self):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        institution_id = educational_institution1.id
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, query_params={"id": institution_id})
            assert response.status_code == 200

        assert response.json == [
            {
                "id": educational_institution1.id,
                "uai": educational_institution1.institutionId,
                "name": educational_institution1.name,
                "postalCode": educational_institution1.postalCode,
                "city": educational_institution1.city,
                "institutionType": educational_institution1.institutionType,
            },
        ]

    @pytest.mark.parametrize("institution_param", ["Spirou Magazine", "Spirou"])
    def test_search_educational_institutions_name(self, institution_param):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(name="Spirou Magazine")
        educational_factories.EducationalInstitutionFactory()

        # test complete name
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, query_params={"name": institution_param})
            assert response.status_code == 200

        assert response.json == [
            {
                "id": educational_institution1.id,
                "uai": educational_institution1.institutionId,
                "name": educational_institution1.name,
                "postalCode": educational_institution1.postalCode,
                "city": educational_institution1.city,
                "institutionType": educational_institution1.institutionType,
            },
        ]

    @pytest.mark.parametrize("city_param", ["et_bim", "bim"])
    def test_search_educational_institutions_city(self, city_param):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(city="et_bim")
        educational_factories.EducationalInstitutionFactory()

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, query_params={"city": city_param})
            assert response.status_code == 200

        assert response.json == [
            {
                "id": educational_institution1.id,
                "uai": educational_institution1.institutionId,
                "name": educational_institution1.name,
                "postalCode": educational_institution1.postalCode,
                "city": educational_institution1.city,
                "institutionType": educational_institution1.institutionType,
            },
        ]

    @pytest.mark.parametrize("institution_type_param", ["et_paf", "paf"])
    def test_search_educational_institutions_institution_type(self, institution_type_param):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(institutionType="et_paf")
        educational_factories.EducationalInstitutionFactory()

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, query_params={"institutionType": institution_type_param})
            assert response.status_code == 200

        assert response.json == [
            {
                "id": educational_institution1.id,
                "uai": educational_institution1.institutionId,
                "name": educational_institution1.name,
                "postalCode": educational_institution1.postalCode,
                "city": educational_institution1.city,
                "institutionType": educational_institution1.institutionType,
            },
        ]

    def test_search_educational_institutions_multiple_filters(self):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(
            name="tralala",
            postalCode="44100",
            city="plouf",
            institutionType="pouet",
        )
        educational_factories.EducationalInstitutionFactory(institutionType="pouet")
        educational_factories.EducationalInstitutionFactory(name="tralala")
        educational_factories.EducationalInstitutionFactory(postalCode="44100")
        educational_factories.EducationalInstitutionFactory(city="plouf")
        educational_factories.EducationalInstitutionFactory()

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(
                plain_api_key,
                query_params={"institutionType": "oue", "name": "rala", "postalCode": "41", "city": "lou"},
            )
            assert response.status_code == 200

        assert response.json == [
            {
                "id": educational_institution1.id,
                "uai": educational_institution1.institutionId,
                "name": educational_institution1.name,
                "postalCode": educational_institution1.postalCode,
                "city": educational_institution1.city,
                "institutionType": educational_institution1.institutionType,
            },
        ]

    def test_limit_educational_institutions(self):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, query_params={"limit": 1})
            assert response.status_code == 200

        assert response.json == [
            {
                "id": educational_institution1.id,
                "uai": educational_institution1.institutionId,
                "name": educational_institution1.name,
                "postalCode": educational_institution1.postalCode,
                "city": educational_institution1.city,
                "institutionType": educational_institution1.institutionType,
            },
        ]

    def test_max_limit_educational_institutions(self):
        plain_api_key, _ = self.setup_provider()

        educational_factories.EducationalInstitutionFactory.create_batch(25)

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, query_params={"limit": 23})
            assert response.status_code == 200

        assert len(response.json) == 20

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert len(response.json) == 20
