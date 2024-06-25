from flask import url_for
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class GetNationalProgramsTest:
    def test_list_national_programs(self, client):
        programs = educational_factories.NationalProgramFactory.create_batch(2)
        offerers_factories.ApiKeyFactory()

        dst = url_for("public_api.v2_prefixed_public_api.get_national_programs")
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(dst)

        assert response.status_code == 200

        program_names = {program["name"] for program in response.json}
        assert program_names == {program.name for program in programs}
