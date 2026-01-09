from pcapi.core import mails
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.users import models as users_models


def get_bonification_granted_email_data(user: users_models.User) -> models.TransactionalEmailData:
    assert user.deposit  # helps mypy

    credit = int(user.deposit.amount)
    bonification_recredits = [
        recredit
        for recredit in user.deposit.recredits
        if recredit.recreditType == finance_models.RecreditType.BONUS_CREDIT
    ]
    if len(bonification_recredits) < 1:
        raise ValueError(f"Couldn't identify bonification recredit for user #{user.id}")

    bonification_recredit = bonification_recredits[0]
    bonification_credit = bonification_recredit.amount
    return models.TransactionalEmailData(
        template=TransactionalEmail.BONIFICATION_GRANTED.value,
        params={
            "CREDIT": credit,
            "FORMATTED_CREDIT": format_price(credit, user, replace_free_amount=False),
            "BONIFICATION_CREDIT": bonification_credit,
            "FORMATTED_BONIFICATION_CREDIT": format_price(bonification_credit, user, replace_free_amount=False),
        },
    )


def send_bonification_granted_email(user: users_models.User) -> None:
    if user.eligibility == users_models.EligibilityType.FREE:
        return

    assert user.deposit  # helps mypy

    has_received_bonus = finance_models.RecreditType.BONUS_CREDIT in [
        recredit.recreditType for recredit in user.deposit.recredits
    ]
    if not has_received_bonus:
        return

    data = get_bonification_granted_email_data(user)
    mails.send(recipients=[user.email], data=data)
