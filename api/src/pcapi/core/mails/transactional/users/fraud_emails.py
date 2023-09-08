from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails import models as mails_models
from pcapi.core.users import models as users_models


def _get_backoffice_user_link(user_id: int) -> str:
    return f'<a href="{settings.BACKOFFICE_URL}/public-accounts/{user_id}">{user_id}</a>'


def _send_fraud_mail(subject: str, header: str, body: str) -> None:
    mails.send(
        recipients=[settings.FRAUD_EMAIL_ADDRESS],
        data=mails_models.TransactionalWithoutTemplateEmailData(
            sender=mails_models.TransactionalSender.DEV,
            subject=subject,
            html_content=f"<h2>{header}</h2><body>{body}</body>",
        ),
    )


def send_duplicate_fraud_detection_mail(user: users_models.User, duplicate: users_models.User) -> None:
    user_backoffice_link = _get_backoffice_user_link(user.id)
    duplicate_backoffice_link = _get_backoffice_user_link(duplicate.id)
    duplicate_got_grant_18 = (
        f" et {duplicate_backoffice_link} a aussi reçu le crédit 18 ans" if duplicate.has_beneficiary_role else ""
    )
    _send_fraud_mail(
        subject="Doublon détecté",
        header="Un doublon a été détecté",
        body=f"""<p>L'utilisateur {user_backoffice_link} essaie d'obtenir son crédit 18 ans. 
Or il semble être un doublon de l'utilisateur {duplicate_backoffice_link}.</p>
<p>Les deux ont déjà été crédités de leur crédit 15-17 ans{duplicate_got_grant_18}.</p>
<p>Ces deux comptes ont donc été suspendus pour suspicion de fraude.</p>""",
    )
