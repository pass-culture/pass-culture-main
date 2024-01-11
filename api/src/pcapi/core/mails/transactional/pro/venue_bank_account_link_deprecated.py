from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_venue_bank_account_link_deprecated_email_data(
    venue_name: str, bank_account_label: str
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.VENUE_BANK_ACCOUNT_LINK_DEPRECATED.value,
        params={
            "VENUE_NAME": venue_name,
            "BANK_ACCOUNT_LABEL": bank_account_label,
        },
    )


def send_venue_bank_account_link_deprecated(venue_name: str, bank_account_label: str, email: str) -> None:
    data = get_venue_bank_account_link_deprecated_email_data(venue_name, bank_account_label)
    mails.send(recipients=[email], data=data)
