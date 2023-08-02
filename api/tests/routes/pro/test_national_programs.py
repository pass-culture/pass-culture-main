from flask import url_for
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class GetNationalProgramsTest:
    def test_get_national_programs(self, client):
        pro = users_factories.ProFactory()
        programs = educational_factories.NationalProgramFactory.create_batch(2)

        client = client.with_session_auth(email=pro.email)
        response = client.get(url_for("Private API.get_national_programs"))

        assert response.status_code == 200

        program_names = {program["name"] for program in response.json}
        assert program_names == {program.name for program in programs}
