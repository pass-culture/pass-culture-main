import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.dms_subscription_emails import (
    send_pre_subscription_from_dms_error_email_to_beneficiary,
)
from pcapi.core.subscription.dms import schemas as dms_schemas


pytestmark = pytest.mark.usefixtures("db_session")


class PreSubscriptionDmsErrorEmailSendinblueTest:
    def test_send_mail(self):
        # Given
        user_mail = "test@exemple.com"
        postal_code = "75"
        id_card_number = "1122"

        field_errors = [
            dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.postal_code, value=postal_code),
            dms_schemas.DmsFieldErrorDetails(
                key=dms_schemas.DmsFieldErrorKeyEnum.id_piece_number, value=id_card_number
            ),
        ]
        # When
        send_pre_subscription_from_dms_error_email_to_beneficiary(user_mail, field_errors)
        # Then
        assert mails_testing.outbox[0]["To"] == user_mail
        assert (
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0]["params"] == {
            "DMS_ERRORS": [
                {"name": "ton code postal", "value": postal_code},
                {"name": "ton numéro de pièce d'identité", "value": id_card_number},
            ],
        }
