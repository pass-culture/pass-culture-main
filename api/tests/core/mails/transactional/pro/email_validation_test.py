from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.email_validation import send_email_validation_to_admin_email
from pcapi.core.mails.transactional.pro.email_validation import send_email_validation_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendProUserValidationEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        user = users_factories.ProFactory()
        user.generate_validation_token()

        # When
        send_email_validation_to_pro_email(user)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value)


class SendAdminUserValidationEmailTest:
    def test_send_mail_to_admin_user(self):
        # Given
        user = users_factories.AdminFactory()
        token = users_factories.PasswordResetTokenFactory(user=user)

        # When
        send_email_validation_to_admin_email(user, token)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value)
