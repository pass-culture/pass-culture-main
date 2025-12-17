from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as user_factories
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.anonymization import get_anonymization_email_data
from pcapi.core.mails.transactional.users.anonymization import send_anonymization_confirmation_email_to_pro


pytestmark = pytest.mark.usefixtures("db_session")


class AnonymizationEmailTest:
    def test_return_correct_email_metadata(self):
        email = get_anonymization_email_data()
        assert email.template == TransactionalEmail.ANONYMIZATION_CONFIRMATION.value

    def test_send_anonymization_confirmation_email_to_pro(self):
        user = user_factories.UserFactory()

        send_anonymization_confirmation_email_to_pro(user.email)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.ANONYMIZATION_CONFIRMATION.value)
        assert mails_testing.outbox[0]["params"] == {}
