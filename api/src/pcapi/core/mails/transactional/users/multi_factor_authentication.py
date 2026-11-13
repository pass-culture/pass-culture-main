from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def send_otp_by_email(user: User, otp: str) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.MFA_OTP_CHALLENGE.value, params={"ONETIMEPASSWORD": otp}
    )
    mails.send(recipients=[user.email], data=data)


def send_failed_mfa_email(user: User) -> None:
    data = models.TransactionalEmailData(template=TransactionalEmail.MFA_FAILED.value)
    mails.send(recipients=[user.email], data=data)
