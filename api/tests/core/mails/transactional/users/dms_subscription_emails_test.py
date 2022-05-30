import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.dms_subscription_emails import (
    send_pre_subscription_from_dms_error_email_to_beneficiary,
)


pytestmark = pytest.mark.usefixtures("db_session")


class PreSubscriptionDmsErrorEmailSendinblueTest:
    def test_send_mail(self):
        # Given
        user_mail = "test@exemple.com"
        postal_code = "75"
        id_card_number = "1122"
        # When
        send_pre_subscription_from_dms_error_email_to_beneficiary(user_mail, postal_code, id_card_number)
        # Then
        assert mails_testing.outbox[0].sent_data["To"] == user_mail
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"] == {
            "POSTAL_CODE": "75",
            "ID_CARD_NUMBER": "1122",
        }
