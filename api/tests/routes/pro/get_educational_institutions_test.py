from typing import Any

import pytest

from pcapi.core.educational.factories import EducationalInstitutionFactory
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_get_educational_institutions(self, client: Any) -> None:
        # Given
        institution1 = EducationalInstitutionFactory(
            name="aaaaaaaaaaaaaaaaa",
            institutionType="toto",
        )
        institution2 = EducationalInstitutionFactory(name="zzzzzzzzzzzzzzzzz", institutionType="tata")
        pro_user = users_factories.ProFactory()

        client.with_session_auth(pro_user.email)
        response = client.get("/educational_institutions")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "educationalInstitutions": [
                {
                    "id": institution1.id,
                    "name": institution1.name,
                    "institutionType": institution1.institutionType,
                    "city": institution1.city,
                    "postalCode": institution1.postalCode,
                },
                {
                    "id": institution2.id,
                    "name": institution2.name,
                    "institutionType": institution2.institutionType,
                    "city": institution2.city,
                    "postalCode": institution2.postalCode,
                },
            ],
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_get_educational_institutions_empty_result(self, client: Any) -> None:
        # Given
        pro_user = users_factories.ProFactory()

        client.with_session_auth(pro_user.email)
        response = client.get("/educational_institutions")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "educationalInstitutions": [],
            "page": 1,
            "pages": 1,
            "total": 0,
        }

    def test_get_educational_institutions_limit(self, client: Any) -> None:
        # Given
        institution1 = EducationalInstitutionFactory()
        EducationalInstitutionFactory()
        pro_user = users_factories.ProFactory()

        client.with_session_auth(pro_user.email)
        response = client.get("/educational_institutions?perPageLimit=1")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "educationalInstitutions": [
                {
                    "id": institution1.id,
                    "name": institution1.name,
                    "institutionType": institution1.institutionType,
                    "city": institution1.city,
                    "postalCode": institution1.postalCode,
                },
            ],
            "page": 1,
            "pages": 2,
            "total": 2,
        }

    def test_get_educational_institutions_limit_page2(self, client: Any) -> None:
        # Given
        EducationalInstitutionFactory()
        EducationalInstitutionFactory()
        institution3 = EducationalInstitutionFactory(
            name="zzzzzzzzzzzzzzz_last_institution",
            institutionType="pouet",
        )
        pro_user = users_factories.ProFactory()

        client.with_session_auth(pro_user.email)
        response = client.get("/educational_institutions?perPageLimit=2&page=2")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "educationalInstitutions": [
                {
                    "id": institution3.id,
                    "name": institution3.name,
                    "institutionType": institution3.institutionType,
                    "city": institution3.city,
                    "postalCode": institution3.postalCode,
                },
            ],
            "page": 2,
            "pages": 2,
            "total": 3,
        }


class Return401Test:
    def test_get_educational_institutions_no_user_login(self, client: Any) -> None:
        # Given
        EducationalInstitutionFactory()
        EducationalInstitutionFactory()

        response = client.get("/educational_institutions")

        # Then
        assert response.status_code == 401
