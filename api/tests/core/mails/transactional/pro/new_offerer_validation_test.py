from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro import new_offerer_validation
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offerers.factories import UserOffererFactory


@pytest.mark.usefixtures("db_session")
class SendNewOffererValidationEmailTest:
    def test_send_mail(self):
        # Given
        offerer = UserOffererFactory(user__email="test@example.com").offerer

        # When
        new_offerer_validation.send_new_offerer_validation_email_to_pro(offerer)

        # Then
        assert mails_testing.outbox[0]["To"] == "test@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.NEW_OFFERER_VALIDATION.value)
        assert mails_testing.outbox[0]["params"] == {"OFFERER_NAME": offerer.name}


@pytest.mark.usefixtures("db_session")
class SendNewOffererRejectionEmailTest:
    def test_send_mail(self):
        # Given
        offerer = UserOffererFactory(
            user__email="test@example.com",
            offerer__rejectionReason=offerer_models.OffererRejectionReason.ADAGE_DECLINED,
        ).offerer

        # When
        new_offerer_validation.send_new_offerer_rejection_email_to_pro(offerer)

        # Then
        assert mails_testing.outbox[0]["To"] == "test@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.NEW_OFFERER_REJECTION.value)
        assert mails_testing.outbox[0]["params"] == {
            "OFFERER_NAME": offerer.name,
            "REJECTION_REASON": "ADAGE_DECLINED",
        }
