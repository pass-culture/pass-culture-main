import pytest

from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.notifications.sms import testing as sms_testing

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_send_phone_validation(app):
    user = UserFactory(isBeneficiary=False, isEmailValidated=True, phoneNumber="060102030405")

    client = TestClient(app.test_client()).with_auth(email=user.email)

    response = client.post("/send_phone_validation_code")

    assert response.status_code == 204
    assert len(sms_testing.requests) == 1

    token = Token.query.filter_by(userId=user.id, type="PHONE_VALIDATION").first()

    response = client.post("/validate_phone_number", {"code": token.value})

    assert response.status_code == 204
    assert User.query.get(user.id).is_phone_validated
