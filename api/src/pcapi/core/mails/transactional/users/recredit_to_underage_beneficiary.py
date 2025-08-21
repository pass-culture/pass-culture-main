from decimal import Decimal

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.users import models as users_models


def get_recredit_to_underage_beneficiary_email_data(
    user: users_models.User,
    recredit_amount: Decimal,
    domains_credit: users_models.DomainsCredit | None,
) -> models.TransactionalEmailData:
    assert domains_credit
    remaining_credit = domains_credit.all.remaining
    assert remaining_credit is not None
    return models.TransactionalEmailData(
        template=TransactionalEmail.RECREDIT_TO_UNDERAGE_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "NEW_CREDIT": recredit_amount,
            "FORMATTED_NEW_CREDIT": format_price(recredit_amount, user, replace_free_amount=False),
            "CREDIT": int(remaining_credit),
            "FORMATTED_CREDIT": format_price(remaining_credit, user, replace_free_amount=False),
        },
    )


def send_recredit_email_to_underage_beneficiary(
    user: users_models.User,
    recredit_amount: Decimal,
    domains_credit: users_models.DomainsCredit | None,
) -> None:
    data = get_recredit_to_underage_beneficiary_email_data(user, recredit_amount, domains_credit)
    mails.send(recipients=[user.email], data=data)


def send_recredit_email_to_18_years_old(
    user: users_models.User,
) -> None:
    data = models.TransactionalEmailData(template=TransactionalEmail.RECREDIT.value)
    mails.send(recipients=[user.email], data=data)
