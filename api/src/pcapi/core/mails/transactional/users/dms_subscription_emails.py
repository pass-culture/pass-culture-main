import typing

from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_create_account_after_dms_email(user_email: str) -> bool:
    return mails.send(
        recipients=[user_email],
        data=SendinblueTransactionalEmailData(template=TransactionalEmail.CREATE_ACCOUNT_AFTER_DMS.value),
    )


def send_complete_subscription_after_dms_email(user_email: str) -> bool:
    return mails.send(
        recipients=[user_email],
        data=SendinblueTransactionalEmailData(template=TransactionalEmail.COMPLETE_SUBSCRIPTION_AFTER_DMS.value),
    )


def send_pre_subscription_from_dms_error_email_to_beneficiary(
    user_email: str, postal_code: typing.Optional[str], id_card_number: typing.Optional[str]
) -> bool:
    if postal_code == None and id_card_number == None:
        return False

    data = SendinblueTransactionalEmailData(template=TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value)
    if postal_code:
        data.params["POSTAL_CODE"] = postal_code
    if id_card_number:
        data.params["ID_CARD_NUMBER"] = id_card_number

    return mails.send(recipients=[user_email], data=data)
