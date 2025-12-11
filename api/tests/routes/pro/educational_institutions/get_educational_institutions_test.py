from typing import Any

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.educational.factories import EducationalInstitutionFactory


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    expected_num_queries = 3
    # get user_session + user
    # count active educational_institution
    # select educational_institution

    def test_get_educational_institutions(self, client: Any) -> None:
        institution1 = EducationalInstitutionFactory(
            name="aaaaaaaaaaaaaaaaa",
            institutionType="toto",
        )
        institution2 = EducationalInstitutionFactory(name="zzzzzzzzzzzzzzzzz", institutionType="tata")
        EducationalInstitutionFactory(isActive=False)
        pro_user = users_factories.ProFactory()

        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(self.expected_num_queries):
            response = client.get("/educational_institutions")
            assert response.status_code == 200

        assert response.json == {
            "educationalInstitutions": [
                {
                    "id": institution1.id,
                    "name": institution1.name,
                    "institutionType": institution1.institutionType,
                    "city": institution1.city,
                    "postalCode": institution1.postalCode,
                    "phoneNumber": institution1.phoneNumber,
                    "institutionId": institution1.institutionId,
                },
                {
                    "id": institution2.id,
                    "name": institution2.name,
                    "institutionType": institution2.institutionType,
                    "city": institution2.city,
                    "postalCode": institution2.postalCode,
                    "phoneNumber": institution2.phoneNumber,
                    "institutionId": institution2.institutionId,
                },
            ],
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_get_educational_institutions_empty_result(self, client: Any) -> None:
        pro_user = users_factories.ProFactory()

        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(self.expected_num_queries):
            response = client.get("/educational_institutions")
            assert response.status_code == 200

        assert response.json == {
            "educationalInstitutions": [],
            "page": 1,
            "pages": 1,
            "total": 0,
        }

    def test_get_educational_institutions_limit(self, client: Any) -> None:
        institution1 = EducationalInstitutionFactory(name="Collège A")
        EducationalInstitutionFactory(name="Collège B")
        pro_user = users_factories.ProFactory()

        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(self.expected_num_queries):
            response = client.get("/educational_institutions?perPageLimit=1")
            assert response.status_code == 200

        assert response.json == {
            "educationalInstitutions": [
                {
                    "id": institution1.id,
                    "name": institution1.name,
                    "institutionType": institution1.institutionType,
                    "city": institution1.city,
                    "postalCode": institution1.postalCode,
                    "phoneNumber": institution1.phoneNumber,
                    "institutionId": institution1.institutionId,
                },
            ],
            "page": 1,
            "pages": 2,
            "total": 2,
        }

    def test_get_educational_institutions_limit_page2(self, client: Any) -> None:
        EducationalInstitutionFactory()
        EducationalInstitutionFactory()
        institution3 = EducationalInstitutionFactory(
            name="zzzzzzzzzzzzzzz_last_institution",
            institutionType="pouet",
        )
        pro_user = users_factories.ProFactory()

        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(self.expected_num_queries):
            response = client.get("/educational_institutions?perPageLimit=2&page=2")
            assert response.status_code == 200

        assert response.json == {
            "educationalInstitutions": [
                {
                    "id": institution3.id,
                    "name": institution3.name,
                    "institutionType": institution3.institutionType,
                    "city": institution3.city,
                    "postalCode": institution3.postalCode,
                    "phoneNumber": institution3.phoneNumber,
                    "institutionId": institution3.institutionId,
                },
            ],
            "page": 2,
            "pages": 2,
            "total": 3,
        }


class Return401Test:
    def test_get_educational_institutions_no_user_login(self, client: Any) -> None:
        EducationalInstitutionFactory()
        EducationalInstitutionFactory()

        with testing.assert_num_queries(0):
            response = client.get("/educational_institutions")
            assert response.status_code == 401
