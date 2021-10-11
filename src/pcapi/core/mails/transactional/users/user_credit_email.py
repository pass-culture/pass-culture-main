from typing import Union

from pcapi.core import mails
from pcapi.core.bookings import conf
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.models.deposit import DepositType
from pcapi.models.feature import FeatureToggle


def get_user_credit_email_data() -> Union[dict, SendinblueTransactionalEmailData]:
    limit_configuration = conf.get_current_limit_configuration_for_type(DepositType.GRANT_18)
    deposit_amount = limit_configuration.TOTAL_CAP
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
    data = get_user_credit_email_data()
    return mails.send(recipients=[user.email], data=data, send_with_sendinblue=True)
