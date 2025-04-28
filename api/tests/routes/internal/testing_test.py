from flask import url_for
import pytest

from pcapi.models import db
from pcapi.models.feature import Feature


pytestmark = pytest.mark.usefixtures("db_session")


class FeaturesToggleTest:
    @pytest.mark.features(ENABLE_NATIVE_APP_RECAPTCHA=False)
    def test_set_features(self, client):
        response = client.patch(
            "/testing/features",
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
        feature = db.session.query(Feature).filter_by(name="ENABLE_NATIVE_APP_RECAPTCHA").one()
        assert feature.isActive


def test_create_adage_jwt_fake_token(client):
    dst = url_for("adage_iframe.create_adage_jwt_fake_token")
    response = client.get(dst)

    assert response.status_code == 200
    assert response.json["token"]


@pytest.mark.settings(ENABLE_TEST_ROUTES=False)
def test_route_unreachable(client):
    dst = url_for("adage_iframe.create_adage_jwt_fake_token")
    response = client.get(dst)
    assert response.status_code == 404
