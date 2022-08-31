from unittest.mock import patch

import pytest

from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.reset_password_to_pro import get_reset_password_to_pro_email_data
from pcapi.core.mails.transactional.pro.reset_password_to_pro import send_reset_password_email_to_pro
from pcapi.core.mails.transactional.pro.reset_password_to_pro import send_reset_password_link_to_admin_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class SendinblueProResetPasswordEmailDataTest:
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

    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_pro_user(
        self,
    ):
        # given
        user = users_factories.ProFactory(email="pro@example.com")
        token = users_factories.ResetPasswordToken(user=user)

        # when
        send_reset_password_email_to_pro(user, token)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.RESET_PASSWORD_TO_PRO.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"
        assert "LIEN_NOUVEAU_MDP" in mails_testing.outbox[0].sent_data["params"]

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
        assert mails_testing.outbox[0].sent_data["subject"] == "Création d'un compte pro"
        assert (
            mails_testing.outbox[0].sent_data["html_content"]
            == "<html><head></head><body><div><div>Bonjour,</div><div>Vous venez de créer le compte de René Coty."
            "</div><div>Le lien de création de mot de passe est <a href='http://exemple.com/reset/?ABCDEFG'>"
            "http://exemple.com/reset/?ABCDEFG</a></div>"
        )
