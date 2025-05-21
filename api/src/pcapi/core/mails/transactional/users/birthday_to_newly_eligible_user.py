from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models


def send_birthday_age_18_email_to_newly_eligible_user_v3(user: users_models.User) -> None:
    from pcapi.core.users.api import get_domains_credit

    remaining_amount = get_domains_credit(user)
    data = models.TransactionalEmailData(
        template=TransactionalEmail.BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER_V3.value,
        params={
            "CREDIT": remaining_amount.all.remaining if remaining_amount else None,
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
