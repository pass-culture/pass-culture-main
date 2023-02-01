from pcapi.core import mails
from pcapi.core.fraud import models as fraud_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


FIELD_ERROR_LABELS = {
    fraud_models.DmsFieldErrorKeyEnum.birth_date: "ta date de naissance",
    fraud_models.DmsFieldErrorKeyEnum.first_name: "ton prénom",
    fraud_models.DmsFieldErrorKeyEnum.id_piece_number: "ton numéro de pièce d'identité",
    fraud_models.DmsFieldErrorKeyEnum.last_name: "ton nom de famille",
    fraud_models.DmsFieldErrorKeyEnum.postal_code: "ton code postal",
}


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
    data.params["DMS_ERRORS"] = [
        {"name": FIELD_ERROR_LABELS.get(error.key), "value": error.value} for error in field_errors
    ]

    return mails.send(recipients=[user_email], data=data)
