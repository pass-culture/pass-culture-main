import pytest


pytestmark = pytest.mark.usefixtures("db_session")


class CookiesConsentTest:
    def test_patch_success(self, client):
        response = client.patch(
            "/native/v1/features_toggle",
            json={
                "features": [
                    {
                        "name": "ENABLE_NATIVE_APP_RECAPTCHA",
                        "isActive": True,
                    }
                ]
            },
        )

        assert response.status_code == 204
