import pytest

from pcapi.core.testing import assert_num_queries


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class StaticTest:
    @pytest.mark.parametrize(
        "path",
        [
            "/static/backoffice/favicon/favicon_default.ico",
            "/static/backoffice/css/bootstrap-icons@1.11.0/font/bootstrap-icons.css",
            "/static/backoffice/fonts/Inter-VariableFont_opsz,wght.ttf",
        ],
    )
    def test_static_file_should_not_make_db_request(self, authenticated_client, path):
        with assert_num_queries(0):
            response = authenticated_client.get(path)
            assert response.status_code == 200
