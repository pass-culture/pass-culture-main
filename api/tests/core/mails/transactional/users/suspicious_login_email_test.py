import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.suspicious_login_email import get_suspicious_login_email_data
from pcapi.core.mails.transactional.users.suspicious_login_email import send_suspicious_login_email


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSuspiciousLoginEmailTest:
    def test_should_return_sendinblue_template_data(self):
        suspicious_email_data = get_suspicious_login_email_data()

        assert suspicious_email_data.template == TransactionalEmail.SUSPICIOUS_LOGIN.value

    def test_should_send_suspicious_login_email(self):
        email = "123@test.com"
        send_suspicious_login_email(email)

        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == email
