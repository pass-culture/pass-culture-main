from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.welcome_to_pro import send_welcome_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendWelcomeToProEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        user = users_factories.ProFactory()
        # When
        send_welcome_to_pro_email(user)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.WELCOME_TO_PRO.value)
