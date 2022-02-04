from typing import Optional

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_pre_subscription_dms_error_email_data(
    postal_code_value: Optional[str], id_card_number: Optional[str]
) -> SendinblueTransactionalEmailData:
    data = SendinblueTransactionalEmailData(template=TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value)

    if postal_code_value:
        data.params["POSTAL_CODE"] = postal_code_value
    if id_card_number:
        data.params["ID_CARD_NUMBER"] = id_card_number
    return data


def send_pre_subscription_from_dms_error_email_to_beneficiary(
    user_email: str, postal_code: Optional[str], id_card_number: Optional[str]
) -> bool:
    if postal_code == None and id_card_number == None:
        return False
    data = get_pre_subscription_dms_error_email_data(postal_code, id_card_number)
    return mails.send(recipients=[user_email], data=data)
