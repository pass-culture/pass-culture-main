import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalInstitutionTest:
    def test_list_educational_institutions(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_institution2 = educational_factories.EducationalInstitutionFactory()
        educational_institution3 = educational_factories.EducationalInstitutionFactory()
        educational_institution4 = educational_factories.EducationalInstitutionFactory()
        educational_institution5 = educational_factories.EducationalInstitutionFactory()
        educational_institution6 = educational_factories.EducationalInstitutionFactory()

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/"
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
            {
                "id": educational_institution2.id,
                "uai": educational_institution2.institutionId,
                "name": educational_institution2.name,
                "postalCode": educational_institution2.postalCode,
                "city": educational_institution2.city,
                "institutionType": educational_institution2.institutionType,
            },
            {
                "id": educational_institution3.id,
                "uai": educational_institution3.institutionId,
                "name": educational_institution3.name,
                "postalCode": educational_institution3.postalCode,
                "city": educational_institution3.city,
                "institutionType": educational_institution3.institutionType,
            },
            {
                "id": educational_institution4.id,
                "uai": educational_institution4.institutionId,
                "name": educational_institution4.name,
                "postalCode": educational_institution4.postalCode,
                "city": educational_institution4.city,
                "institutionType": educational_institution4.institutionType,
            },
            {
                "id": educational_institution5.id,
                "uai": educational_institution5.institutionId,
                "name": educational_institution5.name,
                "postalCode": educational_institution5.postalCode,
                "city": educational_institution5.city,
                "institutionType": educational_institution5.institutionType,
            },
            {
                "id": educational_institution6.id,
                "uai": educational_institution6.institutionId,
                "name": educational_institution6.name,
                "postalCode": educational_institution6.postalCode,
                "city": educational_institution6.city,
                "institutionType": educational_institution6.institutionType,
            },
        ]

    def test_search_educational_institutions_postal_code(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_institution1 = educational_factories.EducationalInstitutionFactory(postalCode="44100")
        educational_factories.EducationalInstitutionFactory()

        # complete postal code
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
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
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
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

    def test_search_educational_institutions_id(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/educational-institutions/?id={educational_institution1.id}"
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

    def test_search_educational_institutions_name(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_institution1 = educational_factories.EducationalInstitutionFactory(name="pouet")
        educational_factories.EducationalInstitutionFactory()

        # test complete name
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/educational-institutions/?name={educational_institution1.name}"
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
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/?name=oue"
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

    def test_search_educational_institutions_city(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_institution1 = educational_factories.EducationalInstitutionFactory(city="pouet")
        educational_factories.EducationalInstitutionFactory()

        # test complete city
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/educational-institutions/?city={educational_institution1.city}"
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
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/?city=oue"
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

    def test_search_educational_institutions_institution_type(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_institution1 = educational_factories.EducationalInstitutionFactory(institutionType="pouet")
        educational_factories.EducationalInstitutionFactory()

        # test complete city
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/educational-institutions/?institutionType={educational_institution1.institutionType}"
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
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/?institutionType=oue"
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

    def test_search_educational_institutions_multiple_filters(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
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
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/?institutionType=oue&name=rala&postalCode=41&city=lou"
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

    def test_limit_educational_institutions(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_institution1 = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/?limit=1"
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

    def test_max_limit_educational_institutions(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalInstitutionFactory()

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/?limit=23"
        )

        # Then
        assert response.status_code == 200
        assert len(response.json) == 20

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/educational-institutions/"
        )

        # Then
        assert response.status_code == 200
        assert len(response.json) == 20

    def test_list_educational_institutions_anonymous_returns_401(self, client):
        # Given

        # When
        response = client.get("/v2/collective/educational-institutions/")

        # Then
        assert response.status_code == 401
