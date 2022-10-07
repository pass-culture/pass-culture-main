from unittest.mock import patch

import pytest

from pcapi.connectors import sirene
import pcapi.core.offerers.factories as offerers_factories

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
@patch("pcapi.routes.pro.validate.maybe_send_offerer_validation_email")
def test_validate_user_token(mocked_maybe_send_offerer_validation_email, app):
    user_offerer = offerers_factories.UserOffererFactory(user__validationToken="token")

    client = TestClient(app.test_client())
    response = client.patch("/validate/user/token")

    assert response.status_code == 204
    assert user_offerer.user.isValidated
    assert user_offerer.user.isEmailValidated

    mocked_maybe_send_offerer_validation_email.assert_called_once_with(
        user_offerer.offerer,
        user_offerer,
        sirene.SirenInfo(
            siren=user_offerer.offerer.siren,
            name="MINISTERE DE LA CULTURE",
            head_office_siret=f"{user_offerer.offerer.siren}00001",
            ape_code="90.03A",
            legal_category_code="1000",
            address=sirene._Address(street="3 RUE DE VALOIS", postal_code="75001", city="Paris"),
        ),
    )


@pytest.mark.usefixtures("db_session")
def test_fail_if_unknown_token(app):
    client = TestClient(app.test_client())
    response = client.patch("/validate/user/unknown-token")

    assert response.status_code == 404
    assert response.json["global"] == ["Ce lien est invalide"]
