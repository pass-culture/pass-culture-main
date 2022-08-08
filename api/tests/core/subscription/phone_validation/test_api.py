from ssl import SSLError
from unittest.mock import patch

import pytest
from sib_api_v3_sdk.rest import ApiException

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
class EnsurePhoneNumberUnicityTest:
    def test_send_phone_code_error_if_validated_by_beneficiary(self):
        users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
            roles=[users_models.UserRole.BENEFICIARY],
        )
        in_validation_user = users_factories.UserFactory()

        with pytest.raises(phone_validation_exceptions.PhoneAlreadyExists):
            phone_validation_api.send_phone_validation_code(in_validation_user, "+33607080900")

        assert users_models.Token.query.count() == 0

    def test_send_phone_code_success_if_validated_by_not_beneficiary(self):
        already_validated_user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
            roles=[],
        )
        in_validation_user = users_factories.UserFactory()

        # 1. send_phone_validation_code is authorized and does not change owner
        phone_validation_api.send_phone_validation_code(in_validation_user, "+33607080900")

        token = users_models.Token.query.filter(users_models.Token.user == in_validation_user).one()
        assert token.type == users_models.TokenType.PHONE_VALIDATION
        assert already_validated_user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED

        # 2. validate_phone_number is authorized and changes owner
        phone_validation_api.validate_phone_number(in_validation_user, token.value)
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

        unvalidated_for_peer_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=in_validation_user.id
        ).one()
        assert unvalidated_for_peer_check.reasonCodes == [fraud_models.FraudReasonCode.PHONE_UNVALIDATION_FOR_PEER]
        assert (
            unvalidated_for_peer_check.reason
            == f"The phone number validation had the following side effect: phone number +33607080900 was unvalidated for user {already_validated_user.id}"
        )


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
