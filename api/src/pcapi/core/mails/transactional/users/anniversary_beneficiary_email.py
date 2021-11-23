from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.payments.api import get_granted_deposit
from pcapi.core.users import models as users_models
from pcapi.core.users.api import get_domains_credit
from pcapi.models.feature import FeatureToggle
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_anniversary_18_user_email_data(user: users_models.User) -> dict:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        email_link = generate_firebase_dynamic_link(path="id-check", params={"email": user.email})
        granted_deposit = get_granted_deposit(user, user.eligibility)
        return {
            "Mj-TemplateID": 2030056,
            "Mj-TemplateLanguage": True,
            "Mj-trackclick": 1,
            "Vars": {
                "nativeAppLink": email_link,
                "depositAmount": int(granted_deposit.amount),
            },
        }

    return SendinblueTransactionalEmailData(template=TransactionalEmail.ANNIVERSARY_18_BENEFICIARY.value)


def send_newly_eligible_18_user_email(user: users_models.User) -> bool:
    data = get_anniversary_18_user_email_data(user)
    return mails.send(recipients=[user.email], data=data)


def get_anniversary_16_17_user_email_data(user: users_models.User) -> dict:
    granted_deposit = get_granted_deposit(user, user.eligibility)
    domains_credit = get_domains_credit(user)

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.ANNIVERSARY_16_17_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "NEW_CREDIT": granted_deposit.amount,
            "CREDIT": int(domains_credit.all.remaining),
        },
    )


def send_newly_eligible_16_17_user_email(user: users_models.User) -> bool:
    data = get_anniversary_16_17_user_email_data(user)
    return mails.send(recipients=[user.email], data=data)
