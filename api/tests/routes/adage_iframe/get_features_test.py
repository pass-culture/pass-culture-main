import pytest

from pcapi.routes.adage_iframe import features

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


class FeaturesTest:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in(self, client):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        response = client.get("/adage-iframe/features")

        # then
        assert response.status_code == 200
        feature_names = {feature_dict["name"] for feature_dict in response.json}
        assert feature_names == {feature.name for feature in features.ADAGE_FEATURES}
        assert "SYNCHRONIZE_ALLOCINE" not in feature_names

    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, client):
        # when
        response = client.get("/adage-iframe/features")

        # then
        assert response.status_code == 401
