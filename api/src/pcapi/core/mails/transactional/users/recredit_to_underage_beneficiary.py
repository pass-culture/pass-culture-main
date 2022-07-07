from decimal import Decimal

from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models
from pcapi.core.users.api import get_domains_credit


def get_recredit_to_underage_beneficiary_email_data(
    user: users_models.User,
    recredit_amount: Decimal,
) -> SendinblueTransactionalEmailData:
    domains_credit = get_domains_credit(user)

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.RECREDIT_TO_UNDERAGE_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "NEW_CREDIT": recredit_amount,
            "CREDIT": int(domains_credit.all.remaining),  # type: ignore [union-attr]
        },
    )


def send_recredit_email_to_underage_beneficiary(user: users_models.User, recredit_amount: Decimal) -> bool:
    data = get_recredit_to_underage_beneficiary_email_data(user, recredit_amount)
    return mails.send(recipients=[user.email], data=data)  # type: ignore [list-item]
