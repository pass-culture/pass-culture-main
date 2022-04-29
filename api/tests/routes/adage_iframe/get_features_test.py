from typing import ByteString

import pytest

from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


def _create_adage_valid_token_with_email(
    email: str,
    civility: str = "Mme",
    lastname: str = "LAPROF",
    firstname: str = "Jeanne",
    uai: str = "EAU123",
) -> ByteString:
    return create_adage_jwt_fake_valid_token(
        civility=civility, lastname=lastname, firstname=firstname, email=email, uai=uai
    )


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in(self, client):
        # given
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        response = client.get("/adage-iframe/features")

        # then
        assert response.status_code == 200
        feature_name_keys = [feature_dict["nameKey"] for feature_dict in response.json]
        assert "SYNCHRONIZE_ALLOCINE" in feature_name_keys


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, client):
        # when
        response = client.get("/adage-iframe/features")

        # then
        assert response.status_code == 403
