from flask import url_for
import pytest

from pcapi.core.testing import override_features


pytestmark = pytest.mark.usefixtures("db_session")


class SearchHelper:
    @property
    def endpoint(self):
        raise NotImplementedError()

    @property
    def search_path(self):
        return url_for(self.endpoint)

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_view_empty_search_page(self, client, legit_user):  # type: ignore
        response = client.with_session_auth(legit_user.email).get(self.search_path)
        assert response.status_code == 200

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_invalid_search(self, client, legit_user):  # type: ignore
        url = url_for(self.endpoint, unknown="param")
        response = client.with_session_auth(legit_user.email).get(url)

        assert response.status_code == 400

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_search(self, client, legit_user):  # type: ignore
        response = client.with_session_auth(legit_user.email).get(self.search_path)
        assert response.status_code == 200
