from flask import url_for
import pytest


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class SearchHelper:
    @property
    def endpoint(self):
        raise NotImplementedError()

    @property
    def search_path(self):
        return url_for(self.endpoint)

    def test_view_empty_search_page(self, client, legit_user):
        response = client.with_bo_session_auth(legit_user).get(self.search_path)
        assert response.status_code == 200

    def test_invalid_search(self, client, legit_user):
        url = url_for(self.endpoint, unknown="param")
        response = client.with_bo_session_auth(legit_user).get(url)

        assert response.status_code == 400

    def test_search(self, client, legit_user):
        response = client.with_bo_session_auth(legit_user).get(self.search_path)
        assert response.status_code == 200
