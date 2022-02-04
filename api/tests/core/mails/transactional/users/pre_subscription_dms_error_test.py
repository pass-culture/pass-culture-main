import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.pre_subscription_dms_error import (
    send_pre_subscription_from_dms_error_email_to_beneficiary,
)
from pcapi.core.mails.transactional.users.pre_subscription_dms_error import get_pre_subscription_dms_error_email_data


pytestmark = pytest.mark.usefixtures("db_session")


class PreSubscriptionDmsErrorEmailSendinblueTest:
    @pytest.mark.parametrize("postal_code,expected_postal_code", [("75", {"POSTAL_CODE": "75"}), (None, {})])
    @pytest.mark.parametrize(
        "id_card_number,expected_id",
        [("1122", {"ID_CARD_NUMBER": "1122"}), (None, {})],
    )
    def test_return_correct_email_metadata(self, postal_code, id_card_number, expected_postal_code, expected_id):
        if postal_code is None and id_card_number is None:
            pass
        else:
            # When
            email = get_pre_subscription_dms_error_email_data(postal_code, id_card_number)
            # Then
            assert email.template == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value
            assert email.params == {**expected_postal_code, **expected_id}

    def test_send_mail(self):
        # Given
        user_mail = "test@exemple.com"
        postal_code = "75"
        id_card_number = "1122"
        # When
        send_pre_subscription_from_dms_error_email_to_beneficiary(user_mail, postal_code, id_card_number)
        # Then
        mails_testing.outbox[0].sent_data["To"] == user_mail
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"] == {
            "POSTAL_CODE": "75",
            "ID_CARD_NUMBER": "1122",
        }
