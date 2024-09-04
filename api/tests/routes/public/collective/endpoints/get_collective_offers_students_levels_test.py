import pytest

from pcapi.core import testing
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetStudentsLevelsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/student-levels"
    endpoint_method = "get"

    def test_list_students_levels(self, client):
        plain_api_key, _ = self.setup_provider()

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select features
        with testing.assert_num_queries(2):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        response_list = response.json
        assert {"id": "GENERAL0", "name": "Lycée - Terminale"} in response_list
        assert response_list == [
            {"id": student_level.name, "name": student_level.value}
            for student_level in educational_models.StudentLevels
        ]

    def test_list_students_levels_user_auth_returns_401(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        client = client.with_session_auth(user_offerer.user.email)
        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
            response = client.get(self.endpoint_url)
            assert response.status_code == 401
