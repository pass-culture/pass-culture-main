import pytest

import pcapi.core.educational.factories as educational_factories
from pcapi.core import testing

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class GetNationalProgramsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/national-programs/"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select national_program

    def test_list_national_programs(self):
        plain_api_key, _ = self.setup_provider()
        active_programs = educational_factories.NationalProgramFactory.create_batch(2)
        educational_factories.NationalProgramFactory(isActive=False)  # inactive program, should not appear in result

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        program_names = {program["name"] for program in response.json}
        assert program_names == {program.name for program in active_programs}
