import pytest

import pcapi.core.educational.models as educational_models
from pcapi.core import testing

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetStudentsLevelsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/student-levels"
    endpoint_method = "get"

    def test_list_students_levels(self, client):
        plain_api_key, _ = self.setup_provider()

        num_queries = 1  # select api_key, offerer and provider
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        response_list = response.json
        assert {"id": "GENERAL0", "name": "Lycée - Terminale"} in response_list
        assert response_list == [
            {"id": student_level.name, "name": student_level.value}
            for student_level in educational_models.StudentLevels
        ]
