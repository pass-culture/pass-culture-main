import pcapi.core.users.models as users_models
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_beneficiary_personal_data_updated(
    user: users_models.User,
    *,
    is_first_name_updated: bool = False,
    is_last_name_updated: bool = False,
    is_email_updated: bool = False,
    is_phone_number_updated: bool = False,
) -> bool:
    updated_fields: set[str] = set()

    # Apply values expected in transactional email template
    if is_first_name_updated:
        updated_fields.add("FIRST_NAME")
    if is_last_name_updated:
        updated_fields.add("LAST_NAME")
    if is_email_updated:
        updated_fields.add("EMAIL")
    if is_phone_number_updated:
        updated_fields.add("PHONE_NUMBER")

    if not updated_fields:
        return False

    data = models.TransactionalEmailData(
        template=TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value,
        params={
            "FIRSTNAME": user.firstName,
            "LASTNAME": user.lastName,
            "UPDATED_FIELD": ",".join(sorted(updated_fields)),
        },
    )
    mails.send(recipients=[user.email], data=data)

    return True
