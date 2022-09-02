from pcapi.core import mails
from pcapi.core.fraud import models as fraud_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_create_account_after_dms_email(user_email: str) -> bool:
    return mails.send(
        recipients=[user_email],
        data=models.TransactionalEmailData(template=TransactionalEmail.CREATE_ACCOUNT_AFTER_DMS.value),
    )


def send_complete_subscription_after_dms_email(user_email: str) -> bool:
    return mails.send(
        recipients=[user_email],
        data=models.TransactionalEmailData(template=TransactionalEmail.COMPLETE_SUBSCRIPTION_AFTER_DMS.value),
    )


def send_pre_subscription_from_dms_error_email_to_beneficiary(
    user_email: str, field_errors: list[fraud_models.DmsFieldErrorDetails]
) -> bool:

    if len(field_errors) == 0:
        return False
    data = models.TransactionalEmailData(template=TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value)

    ### ----- TODO: remove when PROD template is updated to use the new DMS_ERRORS param ------ ###
    postal_code_error = next(
        (error for error in field_errors if error.key == fraud_models.DmsFieldErrorKeyEnum.postal_code), None
    )
    id_card_number_error = next(
        (error for error in field_errors if error.key == fraud_models.DmsFieldErrorKeyEnum.id_piece_number),
        None,
    )
    if postal_code_error:
        data.params["POSTAL_CODE"] = postal_code_error.value
    if id_card_number_error:
        data.params["ID_CARD_NUMBER"] = id_card_number_error.value
    ### --------------------------------------------------------------------------------------- ###

    data.params["DMS_ERRORS"] = [{"name": error.get_field_label(), "value": error.value} for error in field_errors]

    return mails.send(recipients=[user_email], data=data)
