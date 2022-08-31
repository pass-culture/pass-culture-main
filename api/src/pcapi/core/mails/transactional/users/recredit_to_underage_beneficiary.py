from decimal import Decimal

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models


def get_recredit_to_underage_beneficiary_email_data(
    user: users_models.User,
    recredit_amount: Decimal,
    domains_credit: users_models.DomainsCredit | None,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.RECREDIT_TO_UNDERAGE_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "NEW_CREDIT": recredit_amount,
            "CREDIT": int(domains_credit.all.remaining),  # type: ignore [union-attr]
        },
    )


def send_recredit_email_to_underage_beneficiary(
    user: users_models.User,
    recredit_amount: Decimal,
    domains_credit: users_models.DomainsCredit | None,
) -> bool:
    data = get_recredit_to_underage_beneficiary_email_data(user, recredit_amount, domains_credit)
    return mails.send(recipients=[user.email], data=data)
