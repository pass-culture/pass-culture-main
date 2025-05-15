from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.mails.transactional.pro.email_validation import send_signup_email_confirmation_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


pytestmark = pytest.mark.usefixtures("db_session")


class SendProUserValidationEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        user = users_factories.ProFactory()
        token = token_utils.Token.create(token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, ttl=None, user_id=user.id)

        # When
        send_signup_email_confirmation_to_pro(user, token.encoded_token)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.SIGNUP_EMAIL_CONFIRMATION_TO_PRO.value)
        assert mails_testing.outbox[0]["params"] == {
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/validation/{token.encoded_token}",
        }
