import pytest
from flask import url_for


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class SearchHelper:
    @property
    def endpoint(self):
        raise NotImplementedError()

    @property
    def search_path(self):
        return url_for(self.endpoint)

    def test_view_empty_search_page(self, authenticated_client):
        response = authenticated_client.get(self.search_path)
        assert response.status_code == 200

    def test_invalid_search(self, authenticated_client):
        url = url_for(self.endpoint, unknown="param")
        response = authenticated_client.get(url)

        assert response.status_code == 400

    def test_search(self, authenticated_client):
        response = authenticated_client.get(self.search_path)
        assert response.status_code == 200
