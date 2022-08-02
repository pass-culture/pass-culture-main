from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole


def get_accepted_as_beneficiary_email_data(user: User) -> SendinblueTransactionalEmailData:
    if not user.has_active_deposit:
        raise ValueError("Beneficiary should have a deposit")

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value,
        params={
            "CREDIT": int(user.deposit.amount),  # type: ignore [union-attr, arg-type]
        },
    )


def get_accepted_as_underage_beneficiary_email_data(user: User) -> SendinblueTransactionalEmailData:
    if user.has_active_deposit is None:
        raise ValueError("Beneficiary should have a deposit")

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_EAC_BENEFICIARY.value,
        params={
            "FIRSTNAME": user.firstName,
            "CREDIT": int(user.deposit.amount),  # type: ignore [union-attr, arg-type]
        },
    )


def send_accepted_as_beneficiary_email(user: User) -> bool:
    if UserRole.UNDERAGE_BENEFICIARY in user.roles:
        data = get_accepted_as_underage_beneficiary_email_data(user)
    elif UserRole.BENEFICIARY in user.roles:
        data = get_accepted_as_beneficiary_email_data(user)
    else:
        data = None

    if not data:
        return False

    return mails.send(recipients=[user.email], data=data)
