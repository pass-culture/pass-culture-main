from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.users import models as users_models


def send_birthday_age_18_email_to_newly_eligible_user_v3(user: users_models.User) -> None:
    from pcapi.core.users.api import get_domains_credit

    remaining_credit = get_domains_credit(user)
    remaining_amount = remaining_credit.all.remaining if remaining_credit is not None else None
    data = models.TransactionalEmailData(
        template=TransactionalEmail.BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER_V3.value,
        params={
            "CREDIT": remaining_amount,
            "FORMATTED_CREDIT": format_price(remaining_amount, user, replace_free_amount=False)
            if remaining_amount
            else None,
            "DEPOSITS_COUNT": len(user.deposits),
        },
    )
    mails.send(recipients=[user.email], data=data)


def send_birthday_age_17_email_to_newly_eligible_user(user: users_models.User) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.BIRTHDAY_AGE_17_TO_NEWLY_ELIGIBLE_USER.value,
        params={"DEPOSITS_COUNT": len(user.deposits)},
    )
    mails.send(recipients=[user.email], data=data)
