from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription.dms import schemas as dms_schemas


FIELD_ERROR_LABELS = {
    dms_schemas.DmsFieldErrorKeyEnum.birth_date: "ta date de naissance",
    dms_schemas.DmsFieldErrorKeyEnum.first_name: "ton prénom",
    dms_schemas.DmsFieldErrorKeyEnum.id_piece_number: "ton numéro de pièce d'identité",
    dms_schemas.DmsFieldErrorKeyEnum.last_name: "ton nom de famille",
    dms_schemas.DmsFieldErrorKeyEnum.postal_code: "ton code postal",
}


def send_create_account_after_dms_email(user_email: str) -> None:
    mails.send(
        recipients=[user_email],
        data=models.TransactionalEmailData(template=TransactionalEmail.CREATE_ACCOUNT_AFTER_DMS.value),
    )


def send_complete_subscription_after_dms_email(user_email: str) -> None:
    mails.send(
        recipients=[user_email],
        data=models.TransactionalEmailData(template=TransactionalEmail.COMPLETE_SUBSCRIPTION_AFTER_DMS.value),
    )


def send_pre_subscription_from_dms_error_email_to_beneficiary(
    user_email: str, field_errors: list[dms_schemas.DmsFieldErrorDetails]
) -> None:
    if not field_errors:
        return
    data = models.TransactionalEmailData(template=TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value)
    data.params["DMS_ERRORS"] = [
        {"name": FIELD_ERROR_LABELS.get(error.key), "value": error.value} for error in field_errors
    ]

    mails.send(recipients=[user_email], data=data)
