from datetime import datetime
from typing import Union

from dateutil.relativedelta import relativedelta

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.payments import conf as payments_conf
from pcapi.core.payments.models import DepositType
from pcapi.core.users import models as users_models
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.models.feature import FeatureToggle
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_email_confirmation_email_data(
    user: users_models.User, token: users_models.Token
) -> Union[dict, SendinblueTransactionalEmailData]:
    expiration_timestamp = int(token.expirationDate.timestamp())
    email_confirmation_link = generate_firebase_dynamic_link(
        path="signup-confirmation",
        params={"token": token.value, "expiration_timestamp": expiration_timestamp, "email": user.email},
    )
    limit_configuration = payments_conf.get_current_limit_configuration_for_type(DepositType.GRANT_18)
    deposit_amount = limit_configuration.TOTAL_CAP

    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "Mj-TemplateID": 2015423,
            "Mj-TemplateLanguage": True,
            "Mj-campaign": "confirmation-compte",
            "Mj-trackclick": 1,
            "Vars": {
                "nativeAppLink": email_confirmation_link,
                "isEligible": int(user.is_eligible),
                "isMinor": int(user.dateOfBirth + relativedelta(years=18) > datetime.today()),
                "depositAmount": int(deposit_amount),
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_CONFIRMATION.value,
        params={
            "CONFIRMATION_LINK": email_confirmation_link,
        },
    )


def send_email_confirmation_email(
    user: User,
    token: Token,
) -> bool:
    data = get_email_confirmation_email_data(user=user, token=token)
    return mails.send(recipients=[user.email], data=data, send_with_sendinblue=True)
