import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.subscription_document_error import send_subscription_document_error_email
from pcapi.core.testing import override_features


pytestmark = pytest.mark.usefixtures("db_session")


class MailjetSubscriptionErrorEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_unreadable_document_error_email_sendinblue_not_activated(self) -> None:
        email = "123@test.com"
        code = "unread-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2958557
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_foreign_document_error_email_sendinblue_not_activated(self) -> None:
        email = "123@test.com"
        code = "unread-mrz-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 3188025
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_invalid_document_error_email_sendinblue_not_activated(self) -> None:
        email = "123@test.com"
        code = "invalid-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2958584
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_unreadable_document_error_email_by_default_when_wrong_error_code(self) -> None:
        email = "123@test.com"
        code = "information-error"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2958557
        assert mails_testing.outbox[0].sent_data["To"] == email


class SendinblueSubscriptionDocumentErrorEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_information_error_email_by_default_when_wrong_zerror_code(self) -> None:
        email = "123@test.com"
        code = "wrong-code"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_information_error_email(self) -> None:
        email = "123@test.com"
        code = "information-error"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_unreadable_document_error_email(self) -> None:
        email = "123@test.com"
        code = "unread-document"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_invalid_document_error_email(self) -> None:
        email = "123@test.com"
        code = "invalid-document"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INVALID_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_foreign_document_error_email(self) -> None:
        email = "123@test.com"
        code = "unread-mrz-document"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_information_document_error_email(self) -> None:
        email = "123@test.com"
        code = "information-error"
        send_subscription_document_error_email(email, code)

        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == email
