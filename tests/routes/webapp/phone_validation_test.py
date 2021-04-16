from unittest.mock import patch

import pytest

from pcapi.core.users.factories import UserFactory

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.users.api.SendinblueBackend")
def test_send_phone_validation_code(mocked_sendinblue, app):
    user = UserFactory(isBeneficiary=False, isEmailValidated=True, phoneNumber="060102030405")

    mocked_sendinblue().send_transac_sms.return_value = True

    client = TestClient(app.test_client()).with_auth(email=user.email)

    response = client.post("/send_phone_validation_code")

    assert response.status_code == 204
