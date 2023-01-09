from flask import url_for
import pytest


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class HomePageTest:
    def test_view_home_page(self, client):  # type: ignore
        response = client.get(url_for("backoffice_v3_web.home"))
        assert response.status_code == 200
