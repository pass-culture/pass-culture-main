from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole


def get_accepted_as_beneficiary_email_data(user: User) -> models.TransactionalEmailData:
    if not user.has_active_deposit:
        raise ValueError("Beneficiary should have a deposit")

    assert user.deposit  # helps mypy
    return models.TransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value,
        params={
            "CREDIT": int(user.deposit.amount),
        },
    )


def get_accepted_as_underage_beneficiary_email_data(user: User) -> models.TransactionalEmailData:
    if not user.has_active_deposit:
        raise ValueError("Beneficiary should have a deposit")

    assert user.deposit  # helps mypy
    return models.TransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_EAC_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "CREDIT": int(user.deposit.amount),
        },
    )


def send_accepted_as_beneficiary_email(user: User) -> None:
    if UserRole.UNDERAGE_BENEFICIARY in user.roles:
        data = get_accepted_as_underage_beneficiary_email_data(user)
    elif UserRole.BENEFICIARY in user.roles:
        data = get_accepted_as_beneficiary_email_data(user)
    else:
        return

    mails.send(recipients=[user.email], data=data)
