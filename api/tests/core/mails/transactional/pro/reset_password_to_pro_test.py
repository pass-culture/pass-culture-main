from unittest.mock import patch

import pytest

from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.reset_password_to_pro import get_reset_password_to_pro_email_data
from pcapi.core.mails.transactional.pro.reset_password_to_pro import send_reset_password_link_to_admin_email
from pcapi.core.mails.transactional.pro.reset_password_to_pro import send_reset_password_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class MailjetProResetPasswordEmailDataTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    @patch("pcapi.settings.PRO_URL", "http://example.net")
    def test_get_email_correct_metadata(self):
        # Given
        pro = users_factories.ProFactory(email="pro@example.com")
        users_factories.ResetPasswordToken(user=pro, value="ABCDEFG")

        # When
        reset_password_email_data = get_reset_password_to_pro_email_data(user=pro, token=pro.tokens[0])

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 779295,
            "MJ-TemplateLanguage": True,
            "Vars": {"lien_nouveau_mdp": "http://example.net/mot-de-passe-perdu?token=ABCDEFG"},
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_pro_user(
        self,
    ):
        # given
        user = users_factories.ProFactory(email="pro@example.com")

        # when
        send_reset_password_to_pro_email(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 779295


@pytest.mark.usefixtures("db_session")
class SendinblueProResetPasswordEmailDataTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    @patch("pcapi.settings.PRO_URL", "http://example.net")
    def test_get_email_correct_metadata(self):
        # Given
        pro = users_factories.ProFactory(email="pro@example.com")
        users_factories.ResetPasswordToken(user=pro, value="ABCDEFG")

        # When
        reset_password_email_data = get_reset_password_to_pro_email_data(user=pro, token=pro.tokens[0])

        # Then
        assert reset_password_email_data.template == TransactionalEmail.RESET_PASSWORD_TO_PRO.value
        assert reset_password_email_data.params == {
            "LIEN_NOUVEAU_MDP": "http://example.net/mot-de-passe-perdu?token=ABCDEFG"
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_pro_user(
        self,
    ):
        # given
        user = users_factories.ProFactory(email="pro@example.com")

        # when
        send_reset_password_to_pro_email(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.RESET_PASSWORD_TO_PRO.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"
        assert "LIEN_NOUVEAU_MDP" in mails_testing.outbox[0].sent_data["params"]

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_email_sent_to_admin(
        self,
    ):
        # given
        user = users_factories.ProFactory(email="pro@example.com")
        users_factories.ResetPasswordToken(user=user, value="ABCDEFG")
        reset_password_link = "http://exemple.com/reset/?ABCDEFG"

        # when
        send_reset_password_link_to_admin_email(user, user.email, reset_password_link)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"

        assert reset_password_link in mails_testing.outbox[0].sent_data["html_content"]
        assert "subject" in mails_testing.outbox[0].sent_data
        assert "html_content" in mails_testing.outbox[0].sent_data
