import dataclasses

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.offerer_attachment_validation import (
    get_offerer_attachment_validation_email_data,
)
from pcapi.core.mails.transactional.pro.offerer_attachment_validation import (
    send_offerer_attachment_validation_email_to_pro,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class ProOffererAttachmentValidationEmailTest:
    def test_email_data(self):
        # given
        offerer = offerers_factories.OffererFactory(name="Le Théâtre SAS")
        # when
        mail_data = get_offerer_attachment_validation_email_data(offerer)
        # then
        assert mail_data.template == TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value
        assert mail_data.params == {"OFFERER_NAME": "Le Théâtre SAS"}

    def test_send_email(self):
        # given
        user_offerer = offerers_factories.UserOffererFactory(offerer__name="Le Théâtre SAS")
        # when
        send_offerer_attachment_validation_email_to_pro(user_offerer)
        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == user_offerer.user.email
        assert mails_testing.outbox[0].sent_data["params"]["OFFERER_NAME"] == "Le Théâtre SAS"
