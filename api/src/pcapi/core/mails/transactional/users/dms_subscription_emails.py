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
