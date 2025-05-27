import logging

from pcapi.core import mails
from pcapi.core.finance.conf import get_credit_amount_per_age_and_eligibility
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.eligibility_api import get_pre_decree_or_current_eligibility
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User


logger = logging.getLogger(__name__)


def get_accepted_as_beneficiary_email_v3_data(user: User) -> models.TransactionalEmailData:
    assert user.deposit  # helps mypy

    eligibility_to_activate = get_pre_decree_or_current_eligibility(user)
    assert user.age
    amount_to_display = get_credit_amount_per_age_and_eligibility(user.age, eligibility_to_activate)
    if amount_to_display is None:
        amount_to_display = user.deposit.amount
    return models.TransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value,
        params={"CREDIT": int(amount_to_display)},
    )


def send_accepted_as_beneficiary_email(user: User) -> None:
    if user.eligibility == EligibilityType.FREE:
        return

    data = get_accepted_as_beneficiary_email_v3_data(user)
    mails.send(recipients=[user.email], data=data)
