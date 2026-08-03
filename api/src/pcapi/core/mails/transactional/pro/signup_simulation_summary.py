import typing

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.structure_signup_api import EligibilityDocument


def get_signup_simulation_summary_email_data(
    signup_link: str, eligibility_documents: list["EligibilityDocument"]
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.SIGNUP_SIMULATION_SUMMARY.value,
        params={
            "SIGNUP_LINK": signup_link,
            "ELIGIBILITY_DOCUMENTS": [document.name for document in eligibility_documents],
        },
    )


def send_signup_simulation_summary_email(
    email: str, signup_link: str, eligibility_documents: list["EligibilityDocument"]
) -> None:
    data = get_signup_simulation_summary_email_data(signup_link, eligibility_documents)
    mails.send(recipients=[email], data=data)
