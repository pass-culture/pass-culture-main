import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.users.subscription_document_error import send_subscription_document_error_email
from pcapi.core.testing import override_features


class SubscriptionUnreadableDocumentErrorEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_document_error_email(self) -> None:
        email = "123@test.com"
        code = "unread-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["template"] == {
            "id_prod": 304,
            "id_not_prod": 38,
            "tags": ["jeunes_document_illisible"],
            "use_priority_queue": True,
        }
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_document_error_email_sendinblue_not_activated(self) -> None:
        email = "123@test.com"
        code = "unread-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2958557
        assert mails_testing.outbox[0].sent_data["To"] == email


class SubscriptionInvalidDocumentErrorEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_subscription_document_error_email(self) -> None:
        email = "123@test.com"
        code = "invalid-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["template"] == {
            "id_prod": 384,
            "id_not_prod": 39,
            "tags": ["jeunes_document_invalide"],
            "use_priority_queue": True,
        }
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_document_error_email_sendinblue_not_activated(self) -> None:
        email = "123@test.com"
        code = "invalid-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2958584
        assert mails_testing.outbox[0].sent_data["To"] == email


class SubscriptionForeignDocumentErrorEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_document_error_email(self) -> None:
        email = "123@test.com"
        code = "unread-mrz-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["template"] == {
            "id_prod": 385,
            "id_not_prod": 40,
            "tags": ["jeunes_document_etranger"],
            "use_priority_queue": True,
        }
        assert mails_testing.outbox[0].sent_data["To"] == email

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_document_error_email_sendinblue_not_activated(self) -> None:
        email = "123@test.com"
        code = "unread-mrz-document"
        send_subscription_document_error_email(email, code)

        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 3188025
        assert mails_testing.outbox[0].sent_data["To"] == email
