from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.testing import override_settings
from pcapi.core.users.api import create_phone_validation_token
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.notifications.sms import testing as sms_testing

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_send_phone_validation(app):
    """
    Test phone code validation.
    + ensure that a user that has no import operation does not become
    beneficiary.
    """
    user = UserFactory(isEmailValidated=True, phoneNumber="+33601020304")

    client = TestClient(app.test_client()).with_session_auth(email=user.email)

    response = client.post("/send_phone_validation_code")

    assert response.status_code == 204
    assert len(sms_testing.requests) == 1

    token = Token.query.filter_by(userId=user.id, type="PHONE_VALIDATION").first()

    response = client.post("/validate_phone_number", {"code": token.value})

    assert response.status_code == 204

    user = User.query.get(user.id)
    assert user.is_phone_validated
    assert not user.has_beneficiary_role


@pytest.mark.usefixtures("db_session")
def test_send_phone_validation_and_become_beneficiary(app, client):
    """
    Test that a user with an OK Identity FraudCheck becomes a beneficiary once its phone
    number is validated.
    """
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)
    user = UserFactory(
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        isEmailValidated=True,
        phoneNumber="+33601020304",
        hasCompletedIdCheck=True,
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        user=user,
        type=fraud_models.FraudCheckType.USER_PROFILING,
        status=fraud_models.FraudCheckStatus.OK,
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
    )

    client.with_session_auth(email=user.email)

    response = client.post("/send_phone_validation_code")

    assert response.status_code == 204
    assert len(sms_testing.requests) == 1

    token = Token.query.filter_by(userId=user.id, type="PHONE_VALIDATION").first()

    response = client.post("/validate_phone_number", {"code": token.value})

    assert response.status_code == 204

    user = User.query.get(user.id)
    assert user.is_phone_validated
    assert user.has_beneficiary_role


@pytest.mark.usefixtures("db_session")
@override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33607080900"})
def test_send_phone_validation_blocked_number(app):
    user = UserFactory(isEmailValidated=True, phoneNumber="+33607080900")

    client = TestClient(app.test_client()).with_session_auth(email=user.email)

    response = client.post("/send_phone_validation_code")

    assert response.status_code == 400
    assert not sms_testing.requests
    assert response.json["code"] == "INVALID_PHONE_NUMBER"
    assert not Token.query.filter_by(userId=user.id).first()


@pytest.mark.usefixtures("db_session")
@override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33607080900"})
def test_update_phone_number_with_blocked_phone_number(app):
    user = UserFactory(isEmailValidated=True, phoneNumber="+33601020304")

    client = TestClient(app.test_client()).with_session_auth(email=user.email)
    response = client.post("/send_phone_validation_code", json={"phoneNumber": "+33607080900"})

    assert response.status_code == 400
    assert response.json["code"] == "INVALID_PHONE_NUMBER"

    assert not Token.query.filter_by(userId=user.id).first()
    db.session.refresh(user)
    assert user.phoneNumber == "+33601020304"


@pytest.mark.usefixtures("db_session")
@override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33607080900"})
def test_validate_phone_validation_with_blocked_number(app):
    user = UserFactory(isEmailValidated=True, phoneNumber="+33607080900")

    token = create_phone_validation_token(user)
    client = TestClient(app.test_client()).with_session_auth(email=user.email)
    response = client.post("/validate_phone_number", {"code": token.value})

    assert response.status_code == 400
    assert response.json["code"] == "INVALID_PHONE_NUMBER"

    assert not User.query.get(user.id).is_phone_validated
    assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()


@pytest.mark.usefixtures("db_session")
def test_send_phone_validation_with_malformed_number(app):
    # user's phone number should be in international format (E.164): +33601020304
    user = UserFactory(isEmailValidated=True, phoneNumber="0601020304")

    token = create_phone_validation_token(user)
    client = TestClient(app.test_client()).with_session_auth(email=user.email)
    response = client.post("/send_phone_validation_code", {"code": token.value})

    assert response.status_code == 400
    assert response.json["code"] == "INVALID_PHONE_NUMBER"

    assert not User.query.get(user.id).is_phone_validated
    assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()


@pytest.mark.usefixtures("db_session")
def test_validate_phone_with_non_french_number(app):
    user = UserFactory(isEmailValidated=True, phoneNumber="+46766123456")

    token = create_phone_validation_token(user)
    client = TestClient(app.test_client()).with_session_auth(email=user.email)
    response = client.post("/validate_phone_number", {"code": token.value})

    assert response.status_code == 400
    assert response.json["code"] == "INVALID_PHONE_NUMBER"

    assert not User.query.get(user.id).is_phone_validated
    assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()


@pytest.mark.usefixtures("db_session")
def test_send_phone_validation_with_non_french_number(app):
    user = UserFactory(isEmailValidated=True, phoneNumber="+46766123456")

    client = TestClient(app.test_client()).with_session_auth(email=user.email)
    response = client.post("/send_phone_validation_code")

    assert response.status_code == 400
    assert response.json["code"] == "INVALID_PHONE_NUMBER"
    assert not sms_testing.requests
    assert not Token.query.filter_by(userId=user.id, type="PHONE_VALIDATION").first()


@pytest.mark.usefixtures("db_session")
def test_update_phone_number_with_non_french_number(app):
    user = UserFactory(isEmailValidated=True, phoneNumber="+46766123456")

    client = TestClient(app.test_client()).with_session_auth(email=user.email)
    response = client.post("/send_phone_validation_code", json={"phoneNumber": "+46766987654"})

    assert response.status_code == 400
    assert response.json["code"] == "INVALID_PHONE_NUMBER"

    assert not Token.query.filter_by(userId=user.id).first()
    db.session.refresh(user)
    assert user.phoneNumber == "+46766123456"
