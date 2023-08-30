import pytest

import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.ubble.subscription_document_error import (
    send_subscription_document_error_email,
)


class SendinblueSubscriptionDocumentErrorEmailTest:
    def test_send_information_error_email(self) -> None:
        email = "123@test.com"
        code = fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_unreadable_document_error_email(self) -> None:
        email = "123@test.com"
        code = fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_invalid_document_error_email(self) -> None:
        email = "123@test.com"
        code = fraud_models.FraudReasonCode.ID_CHECK_EXPIRED
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INVALID_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_foreign_document_error_email(self) -> None:
        email = "123@test.com"
        code = fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_information_document_error_email(self) -> None:
        email = "123@test.com"
        code = fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email
