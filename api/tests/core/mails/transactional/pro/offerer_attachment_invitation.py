import dataclasses

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.offerer_attachment_invitation import (
    retrieve_data_for_offerer_attachment_invitation_existing_user_with_not_validated_email,
)
from pcapi.core.mails.transactional.pro.offerer_attachment_invitation import (
    retrieve_data_for_offerer_attachment_invitation_existing_user_with_validated_email,
)
from pcapi.core.mails.transactional.pro.offerer_attachment_invitation import (
    retrieve_data_for_offerer_attachment_invitation_new_user,
)
from pcapi.core.mails.transactional.pro.offerer_attachment_invitation import send_offerer_attachment_invitation
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class ProOffererAttachmentInvitationTest:
    def test_email_data_new_user(self):
        offerer = offerers_factories.OffererFactory(name="Le Théâtre SAS")

        mail_data = retrieve_data_for_offerer_attachment_invitation_new_user(offerer)

        assert mail_data.template == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value
        assert mail_data.params == {"OFFERER_NAME": "Le Théâtre SAS"}

    def test_email_data_existing_validated_user(self):
        offerer = offerers_factories.OffererFactory(name="Le Théâtre SAS")

        mail_data = retrieve_data_for_offerer_attachment_invitation_existing_user_with_validated_email(offerer)

        assert (
            mail_data.template == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL.value
        )
        assert mail_data.params == {"OFFERER_NAME": "Le Théâtre SAS"}

    @override_settings(PRO_URL="http://pcpro.com")
    def test_email_data_existing_not_validated_user(self):
        offerer = offerers_factories.OffererFactory(name="Le Théâtre SAS")
        user = users_factories.UserFactory(isEmailValidated=False, validationToken="123ABC")

        mail_data = retrieve_data_for_offerer_attachment_invitation_existing_user_with_not_validated_email(
            offerer, user
        )

        assert (
            mail_data.template
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL.value
        )
        assert mail_data.params == {
            "OFFERER_NAME": "Le Théâtre SAS",
            "EMAIL_VALIDATION_LINK": "http://pcpro.com/inscription/validation/123ABC",
        }

    def test_send_email_new_user(self):
        offerer = offerers_factories.OffererFactory(name="Le Théâtre SAS")

        send_offerer_attachment_invitation(["new.user@example.com"], offerer)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == "new.user@example.com"
        assert mails_testing.outbox[0].sent_data["params"]["OFFERER_NAME"] == "Le Théâtre SAS"

    def test_send_email_existing_validated_user(self):
        offerer = offerers_factories.OffererFactory(name="Le Théâtre SAS")
        user = users_factories.ProFactory()

        send_offerer_attachment_invitation([user.email], offerer, user)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["params"]["OFFERER_NAME"] == "Le Théâtre SAS"

    def test_send_email_existing_not_validated_user(self):
        offerer = offerers_factories.OffererFactory(name="Le Théâtre SAS")
        user = users_factories.UserFactory(isEmailValidated=False, validationToken="123ABC")

        send_offerer_attachment_invitation([user.email], offerer, user)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["params"]["OFFERER_NAME"] == "Le Théâtre SAS"
