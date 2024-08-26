import pytest

from pcapi.core.educational import factories as educational_factories

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalInstitutionTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/educational-institutions/"
    endpoint_method = "get"

    def test_list_educational_institutions(self, client: TestClient):
        # Given
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

        # When
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)

        # Then
        assert response.status_code == 200
        assert response.json == expected_json

    def test_search_educational_institutions_postal_code(self, client: TestClient):
        # Given
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(postalCode="44100")
        educational_factories.EducationalInstitutionFactory()

        # complete postal code
        response = client.with_explicit_token(plain_api_key).get(
            f"/v2/collective/educational-institutions/?postalCode={educational_institution1.postalCode}"
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
        # Given
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        # When
        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url, params={"id": educational_institution1.id}
        )

        # Then
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
        # Given
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(name="pouet")
        educational_factories.EducationalInstitutionFactory()

        # test complete name
        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url, params={"name": educational_institution1.name}
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
        response = client.with_explicit_token(plain_api_key).get("/v2/collective/educational-institutions/?name=oue")

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
        # Given
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(city="pouet")
        educational_factories.EducationalInstitutionFactory()

        # test complete city
        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url, params={"city": educational_institution1.city}
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
        # Given
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory(institutionType="pouet")
        educational_factories.EducationalInstitutionFactory()

        # test complete city
        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url, params={"institutionType": educational_institution1.institutionType}
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
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"institutionType": "oue"})

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
        # Given
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
        # Given
        plain_api_key, _ = self.setup_provider()
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        # When
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"limit": 1})

        # Then
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
        # Given
        plain_api_key, _ = self.setup_provider()

        educational_factories.EducationalInstitutionFactory.create_batch(25)

        # When
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params={"limit": 23})

        # Then
        assert response.status_code == 200
        assert len(response.json) == 20

        # When
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)

        # Then
        assert response.status_code == 200
        assert len(response.json) == 20
