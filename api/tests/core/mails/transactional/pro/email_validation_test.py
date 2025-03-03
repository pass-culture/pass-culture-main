from dataclasses import asdict

import pytest

from pcapi import settings
from pcapi.core import token as token_utils
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.email_validation import send_email_validation_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendProUserValidationEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        user = users_factories.ProFactory()
        token = token_utils.Token.create(token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, ttl=None, user_id=user.id)

        # When
        send_email_validation_to_pro_email(user, token)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value)
        assert mails_testing.outbox[0]["params"] == {
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/validation/{token.encoded_token}",
        }
