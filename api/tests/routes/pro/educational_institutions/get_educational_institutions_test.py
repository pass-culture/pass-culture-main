import pytest

from pcapi.core import testing
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.users import factories as users_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    expected_num_queries = 3
    # get user_session + user
    # count active educational_institution
    # select educational_institution

    def test_get_educational_institutions(self, client: TestClient) -> None:
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

    def test_get_educational_institutions_empty_result(self, client: TestClient) -> None:
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

    def test_get_educational_institutions_limit(self, client: TestClient) -> None:
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

    def test_get_educational_institutions_limit_page2(self, client: TestClient) -> None:
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


class Return400Test:
    @pytest.mark.parametrize(
        "params,error",
        (
            ("perPageLimit=-1&page=2", {"perPageLimit": ["Saisissez un nombre supérieur ou égal à 1"]}),
            ("perPageLimit=1001&page=1", {"perPageLimit": ["Saisissez un nombre inférieur ou égal à 1000"]}),
            ("page=0", {"page": ["Saisissez un nombre supérieur ou égal à 1"]}),
        ),
    )
    def test_invalid_params(self, client: TestClient, params: str, error: dict):
        pro_user = users_factories.ProFactory()
        client = client.with_session_auth(pro_user.email)

        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES + 1):  # rollback
            response = client.get(f"/educational_institutions?{params}")

        assert response.status_code == 400
        assert response.json == error


class Return401Test:
    def test_get_educational_institutions_no_user_login(self, client: TestClient) -> None:
        EducationalInstitutionFactory()
        EducationalInstitutionFactory()

        with testing.assert_num_queries(0):
            response = client.get("/educational_institutions")
            assert response.status_code == 401
