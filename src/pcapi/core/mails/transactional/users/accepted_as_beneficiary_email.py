from typing import Optional
from typing import Union

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models.feature import FeatureToggle


def get_accepted_as_beneficiary_email_data(user: User) -> Union[dict, SendinblueTransactionalEmailData]:
    if not user.has_active_deposit:
        raise ValueError("Beneficiary should have a deposit")

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
        template=TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value,
        params={
            "CREDIT": int(deposit_amount),
        },
    )


def get_accepted_as_underage_beneficiary_email_data(user: User) -> Optional[SendinblueTransactionalEmailData]:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return None

    if user.has_active_deposit is None:
        raise ValueError("Beneficiary should have a deposit")

    deposit_amount = user.deposit.amount
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_EAC_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "CREDIT": int(deposit_amount),
        },
    )


def send_accepted_as_beneficiary_email(user: User) -> bool:
    if UserRole.UNDERAGE_BENEFICIARY in user.roles:
        data = get_accepted_as_underage_beneficiary_email_data(user)
    elif UserRole.BENEFICIARY in user.roles:
        data = get_accepted_as_beneficiary_email_data(user)
    else:
        data = None

    if not data:
        return False

    return mails.send(recipients=[user.email], data=data, send_with_sendinblue=True)
