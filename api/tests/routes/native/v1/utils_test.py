import pytest
import semver

from pcapi.core.testing import override_settings

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class CheckClientVersionTest:
    def test_with_invalid_version(self, app):
        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/signin", json={}, headers={"app-version": "caramba"})
        assert response.status_code == 403
        assert response.content_type == "application/json"
        assert response.json == {"code": "UPGRADE_REQUIRED"}

    @override_settings(NATIVE_APP_MINIMAL_CLIENT_VERSION=semver.VersionInfo.parse("1.0.1"))
    def test_with_exact_version(self, app):
        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/signin", json={}, headers={"app-version": "1.0.1"})
        assert response.status_code == 400
        assert response.json == {
            "identifier": ["Ce champ est obligatoire"],
            "password": ["Ce champ est obligatoire"],
        }

    @override_settings(NATIVE_APP_MINIMAL_CLIENT_VERSION=semver.VersionInfo.parse("1.0.1"))
    def test_with_newer_version(self, app):
        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/signin", json={}, headers={"app-version": "1.0.2"})
        assert response.status_code == 400
        assert response.json == {
            "identifier": ["Ce champ est obligatoire"],
            "password": ["Ce champ est obligatoire"],
        }

    @override_settings(NATIVE_APP_MINIMAL_CLIENT_VERSION=semver.VersionInfo.parse("1.0.1"))
    def test_with_older_version(self, app):
        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/signin", json={}, headers={"app-version": "1.0.0"})
        assert response.status_code == 403
        assert response.json == {"code": "UPGRADE_REQUIRED"}
