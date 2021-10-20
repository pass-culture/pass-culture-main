from typing import Union

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.models.feature import FeatureToggle


def get_user_credit_email_data(user: User) -> Union[dict, SendinblueTransactionalEmailData]:
    if not user.has_active_deposit:
        raise Exception("The user has no active deposit")
    deposit_amount = user.deposit.amount

    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "Mj-TemplateID": 2016025,
            "Mj-TemplateLanguage": True,
            "Mj-campaign": "confirmation-credit",
            "Vars": {
                "depositAmount": int(deposit_amount),
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.GRANT_USER_CREDIT,
        params={
            "CREDIT": int(deposit_amount),
        },
    )


def send_user_credit_email(user: User) -> bool:
    data = get_user_credit_email_data(user)
    return mails.send(recipients=[user.email], data=data, send_with_sendinblue=True)
