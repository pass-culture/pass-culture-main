from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.payments.api import get_granted_deposit
from pcapi.core.users import models as users_models
from pcapi.core.users.api import get_domains_credit


def get_recredit_to_underage_beneficiary_email_data(
    user: users_models.User,
) -> SendinblueTransactionalEmailData:
    granted_deposit = get_granted_deposit(user, user.eligibility)
    domains_credit = get_domains_credit(user)

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.RECREDIT_TO_UNDERAGE_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "NEW_CREDIT": granted_deposit.amount,
            "CREDIT": int(domains_credit.all.remaining),
        },
    )


def send_recredit_email_to_underage_beneficiary(user: users_models.User) -> bool:
    data = get_recredit_to_underage_beneficiary_email_data(user)
    return mails.send(recipients=[user.email], data=data)
