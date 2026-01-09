from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models


def get_bonification_declined_email_data(user: users_models.User) -> models.TransactionalEmailData:
    qf_bonus_checks = [
        check
        for check in user.beneficiaryFraudChecks
        if check.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT
    ]
    ko_bonus_checks = [check for check in qf_bonus_checks if check.status == subscription_models.FraudCheckStatus.KO]
    if len(ko_bonus_checks) < 1:
        raise ValueError(f"Couldn't identify bonification ko fraud check for user #{user.id}")

    ko_bonus_check = ko_bonus_checks[0]
    ko_reasons = ko_bonus_check.reasonCodes or []
    if len(ko_reasons) != 1:
        raise ValueError(f"Couldn't identify bonification ko reason for user #{user.id}")
    ko_reason = ko_reasons[0]
    return models.TransactionalEmailData(
        template=TransactionalEmail.BONIFICATION_DECLINED.value,
        params={
            "REASON": ko_reason,
        },
    )


def send_bonification_declined_email(user: users_models.User) -> None:
    if user.eligibility == users_models.EligibilityType.FREE:
        return

    data = get_bonification_declined_email_data(user)
    mails.send(recipients=[user.email], data=data)
