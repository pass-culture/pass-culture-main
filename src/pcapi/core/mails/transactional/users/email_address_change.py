from typing import Union

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.models.feature import FeatureToggle


def get_information_email_change_data(first_name: str) -> Union[dict, SendinblueTransactionalEmailData]:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 2066067,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "beneficiary_name": first_name,
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_ADDRESS_CHANGE_REQUEST,
        params={
            "FIRSTNAME": first_name,
        },
    )


def send_information_email_change_email(user: User) -> bool:
    data = get_information_email_change_data(user.firstName)
    return mails.send(recipients=[user.email], data=data, send_with_sendinblue=True)


def get_confirmation_email_change_data(
    first_name: str, confirmation_link: str
) -> Union[dict, SendinblueTransactionalEmailData]:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 2066065,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "beneficiary_name": first_name,
                "confirmation_link": confirmation_link,
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_ADDRESS_CHANGE_CONFIRMATION,
        params={"FIRSTNAME": first_name, "CONFIRMATION_LINK": confirmation_link},
    )


def send_confirmation_email_change_email(user: User, new_email: str, confirmation_link: str) -> bool:
    data = get_confirmation_email_change_data(user.firstName, confirmation_link)
    return mails.send(recipients=[new_email], data=data, send_with_sendinblue=True)
