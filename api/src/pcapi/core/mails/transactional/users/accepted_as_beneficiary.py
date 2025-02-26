import logging

from pcapi.core import mails
from pcapi.core.finance import api as finance_api
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


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


def get_accepted_as_beneficiary_email_v3_data(user: User) -> models.TransactionalEmailData:
    assert user.deposit  # helps mypy

    recredit = finance_api.get_latest_age_related_user_recredit(user)
    credited_amount = recredit.amount if recredit else user.deposit.amount
    return models.TransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value,
        params={"CREDIT": int(credited_amount)},
    )


def send_accepted_as_beneficiary_email(user: User) -> None:
    data = None
    if FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        data = get_accepted_as_beneficiary_email_v3_data(user)
    else:
        if UserRole.UNDERAGE_BENEFICIARY in user.roles:
            data = get_accepted_as_underage_beneficiary_email_data(user)
        elif UserRole.BENEFICIARY in user.roles:
            data = get_accepted_as_beneficiary_email_data(user)

    if not data:
        logger.error("Could not send activation email to user %s", user.id)
        return
    mails.send(recipients=[user.email], data=data)
