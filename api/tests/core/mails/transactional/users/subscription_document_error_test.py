import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.subscription_document_error import send_subscription_document_error_email


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSubscriptionDocumentErrorEmailTest:
    def test_send_information_error_email_by_default_when_wrong_zerror_code(self) -> None:
        email = "123@test.com"
        code = "wrong-code"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_information_error_email(self) -> None:
        email = "123@test.com"
        code = "information-error"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_unreadable_document_error_email(self) -> None:
        email = "123@test.com"
        code = "unread-document"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_invalid_document_error_email(self) -> None:
        email = "123@test.com"
        code = "invalid-document"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INVALID_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_foreign_document_error_email(self) -> None:
        email = "123@test.com"
        code = "unread-mrz-document"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    def test_send_information_document_error_email(self) -> None:
        email = "123@test.com"
        code = "information-error"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email
