from typing import Union

from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.payments import api as payments_api
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_birthday_age_18_to_newly_eligible_user_email_data(
    user: users_models.User,
) -> Union[dict, SendinblueTransactionalEmailData]:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        email_link = generate_firebase_dynamic_link(path="id-check", params={"email": user.email})
        granted_deposit = payments_api.get_granted_deposit(
            user, user.eligibility, user_age_at_registration=users_api.get_user_age_at_registration(user)
        )
        return {
            "Mj-TemplateID": 2030056,
            "Mj-TemplateLanguage": True,
            "Mj-trackclick": 1,
            "Vars": {
                "nativeAppLink": email_link,
                "depositAmount": int(granted_deposit.amount),
            },
        }

    return SendinblueTransactionalEmailData(template=TransactionalEmail.BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER.value)


def send_birthday_age_18_email_to_newly_eligible_user(user: users_models.User) -> bool:
    data = get_birthday_age_18_to_newly_eligible_user_email_data(user)
    return mails.send(recipients=[user.email], data=data)
