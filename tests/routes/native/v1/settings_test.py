import pytest

from pcapi.core.testing import override_features

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class SettingsTest:
    @override_features(APPLY_BOOKING_LIMITS_V2=False)
    def test_get_settings_before_generalization(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")

        assert response.status_code == 200
        assert response.json == {"depositAmount": 50000}

    @override_features(APPLY_BOOKING_LIMITS_V2=True)
    def test_get_settings_after_generalization(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")

        assert response.status_code == 200
        assert response.json == {"depositAmount": 30000}
