from tests.conftest import TestClient


class RedirectToNativeTest:
    def test_redirect(self, app):
        test_client = TestClient(app.test_client())
        response = test_client.get("/native/v1/redirect_to_native/mot-de-passe-perdu?token=abccontrepoirot")
        assert response.status_code == 302
        assert (
            response.location == "https://app-native.testing.internal-passculture.app"
            "/mot-de-passe-perdu?token=abccontrepoirot"
        )
