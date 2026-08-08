from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.pro.email_validation import send_signup_email_confirmation_to_pro
from pcapi.core.offerers import models as offerers_models


pytestmark = pytest.mark.usefixtures("db_session")


class SendProUserValidationEmailTest:
    def test_sends_email_to_pro_user(self):
        user = users_factories.ProFactory()
        token = token_utils.Token.create(token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, ttl=None, user_id=user.id)

        send_signup_email_confirmation_to_pro(user, token.encoded_token)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.SIGNUP_EMAIL_CONFIRMATION_TO_PRO.value)
        assert mails_testing.outbox[0]["params"] == {
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/compte/confirmation/{token.encoded_token}",
        }

    def test_sends_email_to_pro_user_with_simulation_infos(self):
        user = users_factories.ProFactory()
        token = token_utils.Token.create(token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, ttl=None, user_id=user.id)
        structure_simulation_infos = {
            "siret": "44285836100029",
            "is_open_to_public": True,
            "targets": [offerers_models.TargetAudience.INDIVIDUAL],
            "activity": offerers_models.Activity.MUSEUM,
        }

        send_signup_email_confirmation_to_pro(user, token.encoded_token, structure_simulation_infos)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.SIGNUP_EMAIL_CONFIRMATION_TO_PRO.value)
        assert mails_testing.outbox[0]["params"] == {
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/compte/confirmation/{token.encoded_token}?siret=44285836100029&isOpenToPublic=true&targets=INDIVIDUAL&activity=MUSEUM",
        }
