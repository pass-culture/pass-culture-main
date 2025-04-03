from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models


def send_beneficiary_update_request_reject_for_duplicate_email(
    user_request: users_models.UserAccountUpdateRequest,
) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_DUPLICATE_EMAIL.value,
        params={"DS_APPLICATION_NUMBER": user_request.dsApplicationId},
    )
    mails.send(recipients=[user_request.email], data=data)


def send_beneficiary_update_request_reject_for_already_used_email(
    user_request: users_models.UserAccountUpdateRequest,
) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_ALREADY_USED_EMAIL.value,
        params={"DS_APPLICATION_NUMBER": user_request.dsApplicationId},
    )
    mails.send(recipients=[user_request.email], data=data)


def send_beneficiary_update_request_reject_for_duplicate_phone_number(
    user_request: users_models.UserAccountUpdateRequest,
) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_DUPLICATE_PHONE_NUMBER.value,
        params={"DS_APPLICATION_NUMBER": user_request.dsApplicationId},
    )
    mails.send(recipients=[user_request.email], data=data)


def send_beneficiary_update_request_reject_for_already_used_phone_number(
    user_request: users_models.UserAccountUpdateRequest,
) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_ALREADY_USED_PHONE_NUMBER.value,
        params={"DS_APPLICATION_NUMBER": user_request.dsApplicationId},
    )
    mails.send(recipients=[user_request.email], data=data)


def send_beneficiary_update_request_reject_for_duplicate_full_name(
    user_request: users_models.UserAccountUpdateRequest,
) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_DUPLICATE_FULL_NAME.value,
        params={"DS_APPLICATION_NUMBER": user_request.dsApplicationId},
    )
    mails.send(recipients=[user_request.email], data=data)
