import pytest

from pcapi.core import testing
from pcapi.core.educational import factories as educational_factories

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalInstitutionTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/educational-institutions/"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select educational_institution

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_list_educational_institutions(self, client: TestClient):
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
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert response.json == expected_json

    def test_search_educational_institutions_postal_code(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(postalCode="44100")
        educational_factories.EducationalInstitutionFactory()

        # complete postal code
        postal_code = educational_institution1.postalCode
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(
                f"/v2/collective/educational-institutions/?postalCode={postal_code}"
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

        # partial postal code
        response = client.with_explicit_token(plain_api_key).get(
            "/v2/collective/educational-institutions/?postalCode=41"
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

    def test_search_educational_institutions_id(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        institution_id = educational_institution1.id
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"id": institution_id})
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

    def test_search_educational_institutions_name(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(name="pouet")
        educational_factories.EducationalInstitutionFactory()

        institution_name = educational_institution1.name
        # test complete name
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url, params={"name": institution_name}
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

        # test incomplete name
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"name": "oue"})
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

    def test_search_educational_institutions_city(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(city="pouet")
        educational_factories.EducationalInstitutionFactory()

        institution_city = educational_institution1.city
        # test complete city
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url, params={"city": institution_city}
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

        # test incomplete city
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"city": "oue"})
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

    def test_search_educational_institutions_institution_type(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(institutionType="pouet")
        educational_factories.EducationalInstitutionFactory()

        # test complete city
        institution_type = educational_institution1.institutionType
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url, params={"institutionType": institution_type}
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

        # test incomplete city

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url, params={"institutionType": "oue"}
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

    def test_search_educational_institutions_multiple_filters(self, client: TestClient):
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

        # test incomplete city
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url, params={"institutionType": "oue", "name": "rala", "postalCode": "41", "city": "lou"}
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

    def test_limit_educational_institutions(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"limit": 1})
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

    def test_max_limit_educational_institutions(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()

        educational_factories.EducationalInstitutionFactory.create_batch(25)

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"limit": 23})
            assert response.status_code == 200

        assert len(response.json) == 20

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert len(response.json) == 20
