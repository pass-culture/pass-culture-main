import pytest

from pcapi.core.users.factories import BeneficiaryImportFactory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.notifications.sms import testing as sms_testing

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_send_phone_validation(app):
    """
    Test phone code validation.
    + ensure that a user that has no import operation does not become
    beneficiary.
    """
    user = UserFactory(isBeneficiary=False, isEmailValidated=True, phoneNumber="060102030405")

    client = TestClient(app.test_client()).with_auth(email=user.email)

    response = client.post("/send_phone_validation_code")

    assert response.status_code == 204
    assert len(sms_testing.requests) == 1

    token = Token.query.filter_by(userId=user.id, type="PHONE_VALIDATION").first()

    response = client.post("/validate_phone_number", {"code": token.value})

    assert response.status_code == 204

    user = User.query.get(user.id)
    assert user.is_phone_validated
    assert not user.isBeneficiary


@pytest.mark.usefixtures("db_session")
def test_send_phone_validation_and_become_beneficiary(app):
    """
    Test that a user with a CREATED import becomes a beneficiary once its phone
    number is vaidated.
    """
    user = UserFactory(isBeneficiary=False, isEmailValidated=True, phoneNumber="060102030405")
    beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
    beneficiary_import.setStatus(ImportStatus.CREATED)

    client = TestClient(app.test_client()).with_auth(email=user.email)

    response = client.post("/send_phone_validation_code")

    assert response.status_code == 204
    assert len(sms_testing.requests) == 1

    token = Token.query.filter_by(userId=user.id, type="PHONE_VALIDATION").first()

    response = client.post("/validate_phone_number", {"code": token.value})

    assert response.status_code == 204

    user = User.query.get(user.id)
    assert user.is_phone_validated
    assert user.isBeneficiary
