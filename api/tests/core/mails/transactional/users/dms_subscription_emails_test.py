import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.dms_subscription_emails import (
    send_pre_subscription_from_dms_error_email_to_beneficiary,
)
from pcapi.core.subscription.dms import models as dms_models


pytestmark = pytest.mark.usefixtures("db_session")


class PreSubscriptionDmsErrorEmailSendinblueTest:
    def test_send_mail(self):
        # Given
        user_mail = "test@exemple.com"
        postal_code = "75"
        id_card_number = "1122"

        field_errors = [
            dms_models.DmsFieldErrorDetails(key=dms_models.DmsFieldErrorKeyEnum.postal_code, value=postal_code),
            dms_models.DmsFieldErrorDetails(key=dms_models.DmsFieldErrorKeyEnum.id_piece_number, value=id_card_number),
        ]
        # When
        send_pre_subscription_from_dms_error_email_to_beneficiary(user_mail, field_errors)
        # Then
        assert mails_testing.outbox[0].sent_data["To"] == user_mail
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"] == {
            "POSTAL_CODE": postal_code,
            "ID_CARD_NUMBER": id_card_number,
            "DMS_ERRORS": [
                {"name": "ton code postal", "value": postal_code},
                {"name": "ta pièce d'identité", "value": id_card_number},
            ],
        }
