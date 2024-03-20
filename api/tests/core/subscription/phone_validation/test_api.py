from ssl import SSLError
from unittest.mock import patch

import pytest
from sib_api_v3_sdk.rest import ApiException

from pcapi.core import token as token_utils
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.api import create_phone_validation_token


@pytest.mark.usefixtures("db_session")
class EnsurePhoneNumberUnicityTest:
    def test_send_phone_code_error_if_validated_by_beneficiary(self):
        users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33607080900",
            roles=[users_models.UserRole.BENEFICIARY],
        )
        in_validation_user = users_factories.UserFactory()

        with pytest.raises(phone_validation_exceptions.PhoneAlreadyExists):
            phone_validation_api.send_phone_validation_code(in_validation_user, "+33607080900")

        token_utils.Token.token_exists(token_utils.TokenType.PHONE_VALIDATION, in_validation_user.id)

    @patch(
        "pcapi.notifications.sms.backends.sendinblue.sib_api_v3_sdk.TransactionalSMSApi.send_transac_sms",
    )
    @override_settings(SMS_NOTIFICATION_BACKEND="pcapi.notifications.sms.backends.sendinblue.SendinblueBackend")
    def test_send_phone_code_success_if_validated_by_not_beneficiary(self, send_sms_mock):
        already_validated_user = users_factories.EligibleUnderageFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33607080900",
            roles=[],
        )
        in_validation_user = users_factories.EligibleGrant18Factory()

        # 1. send_phone_validation_code is authorized and does not change owner
        phone_validation_api.send_phone_validation_code(in_validation_user, "+33607080900")

        token = send_sms_mock.call_args[0][0].content[:6]
        assert already_validated_user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED

        # 2. validate_phone_number is authorized and changes owner
        phone_validation_api.validate_phone_number(in_validation_user, token)
        assert already_validated_user.phoneValidationStatus == users_models.PhoneValidationStatusType.UNVALIDATED
        assert in_validation_user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED

        unvalidated_by_peer_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=already_validated_user.id
        ).one()
        assert unvalidated_by_peer_check.reasonCodes == [fraud_models.FraudReasonCode.PHONE_UNVALIDATED_BY_PEER]
        assert (
            unvalidated_by_peer_check.reason
            == f"Phone number +33607080900 was unvalidated by user {in_validation_user.id}"
        )
        assert unvalidated_by_peer_check.eligibilityType == users_models.EligibilityType.UNDERAGE

        unvalidated_for_peer_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=in_validation_user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        ).one()

        assert unvalidated_for_peer_check.reasonCodes == [fraud_models.FraudReasonCode.PHONE_UNVALIDATION_FOR_PEER]
        assert (
            unvalidated_for_peer_check.reason
            == f"The phone number validation had the following side effect: phone number +33607080900 was unvalidated for user {already_validated_user.id}"
        )
        assert unvalidated_for_peer_check.eligibilityType == users_models.EligibilityType.AGE18

        success_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=in_validation_user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
        ).one()
        assert success_check.reasonCodes is None


@pytest.mark.usefixtures("db_session")
class SendSMSTest:
    @patch(
        "pcapi.notifications.sms.backends.sendinblue.sib_api_v3_sdk.TransactionalSMSApi.send_transac_sms",
    )
    @override_settings(SMS_NOTIFICATION_BACKEND="pcapi.notifications.sms.backends.sendinblue.SendinblueBackend")
    def test_send_sms_success(self, mock, app):
        user = users_factories.UserFactory()

        phone_validation_api.send_phone_validation_code(user, "+33600000000")

        assert app.redis_client.get(f"sent_SMS_counter_user_{user.id}") == "1"

    @patch(
        "pcapi.notifications.sms.backends.sendinblue.sib_api_v3_sdk.TransactionalSMSApi.send_transac_sms",
    )
    @patch("secrets.randbelow")
    @override_settings(SMS_NOTIFICATION_BACKEND="pcapi.notifications.sms.backends.sendinblue.SendinblueBackend")
    def test_send_sms_phone_number_with_space(self, randbelow_mock, send_sms_mock):
        user = users_factories.UserFactory()
        randbelow_mock.return_value = "123456"

        phone_validation_api.send_phone_validation_code(user, "+33 6 00 00 00 00")

        assert send_sms_mock.call_args[0][0].content == "123456 est ton code de confirmation pass Culture"
        assert send_sms_mock.call_args[0][0].recipient == "33600000000"
        assert send_sms_mock.call_args[0][0].sender == "PassCulture"
        assert send_sms_mock.call_args[0][0].tag == "phone-validation"
        assert send_sms_mock.call_args[0][0].type == "transactional"
        assert send_sms_mock.call_args[0][0].unicode_enabled is False
        assert send_sms_mock.call_args[0][0].web_url is None

        assert user.phoneNumber == "+33600000000"

    @patch(
        "pcapi.notifications.sms.backends.sendinblue.sib_api_v3_sdk.TransactionalSMSApi.send_transac_sms",
    )
    @override_settings(SMS_NOTIFICATION_BACKEND="pcapi.notifications.sms.backends.sendinblue.SendinblueBackend")
    def test_send_sms_bad_request(self, send_sms_mock, caplog, app):
        user = users_factories.UserFactory()
        send_sms_mock.side_effect = ApiException(status=400)

        with pytest.raises(phone_validation_exceptions.PhoneVerificationException):
            phone_validation_api.send_phone_validation_code(user, "+33600000000")

        assert app.redis_client.get(f"sent_SMS_counter_user_{user.id}") is None

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Error while sending SMS"
        assert caplog.records[0].levelname == "ERROR"

    @patch(
        "pcapi.notifications.sms.backends.sendinblue.sib_api_v3_sdk.TransactionalSMSApi.send_transac_sms",
    )
    @override_settings(SMS_NOTIFICATION_BACKEND="pcapi.notifications.sms.backends.sendinblue.SendinblueBackend")
    def test_retry_success(self, send_sms_mock, caplog, app):
        user = users_factories.UserFactory()
        send_sms_mock.side_effect = [SSLError(), ApiException(status=524), True]

        phone_validation_api.send_phone_validation_code(user, "+33600000000")

        assert app.redis_client.get(f"sent_SMS_counter_user_{user.id}") == "1"

        assert len(caplog.records) == 2
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message == "Exception caught while sending SMS"
        assert caplog.records[1].levelname == "WARNING"
        assert caplog.records[1].message == "Sendinblue replied with status=524 when sending SMS"


@pytest.mark.usefixtures("db_session")
@override_settings(DISABLE_PHONE_VALIDATION_FOR_E2E_TESTS=True)
class BypassPhoneValidationTest:
    def test_bypass_if_email_has_e2e_suffix(self):
        user = users_factories.UserFactory(email="x+e2e@example.com")
        create_phone_validation_token(user, "+33600000000")

        phone_validation_api.validate_phone_number(user, "wrong-code")

        assert user.phoneNumber == "+33600000000"
        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED
        phone_validation_fraud_check = user.beneficiaryFraudChecks[-1]
        assert phone_validation_fraud_check.type == fraud_models.FraudCheckType.PHONE_VALIDATION
        assert phone_validation_fraud_check.status == fraud_models.FraudCheckStatus.OK

    def test_doesnt_validate_if_email_doesnt_have_e2e_suffix_and_code_is_wrong(self):
        user = users_factories.UserFactory(email="x@example.com")
        create_phone_validation_token(user, "+33600000000")

        with pytest.raises(phone_validation_exceptions.NotValidCode):
            phone_validation_api.validate_phone_number(user, "wrong-code")

        assert user.phoneNumber is None
        assert user.phoneValidationStatus is None
