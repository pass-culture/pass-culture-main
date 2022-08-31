from datetime import datetime

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.models as users_models
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.mailing import build_pc_pro_reset_password_link


def get_reset_password_to_pro_email_data(
    user: users_models.User, token: users_models.Token
) -> models.TransactionalEmailData:
    reinit_password_url = build_pc_pro_reset_password_link(token.value)
    return models.TransactionalEmailData(
        template=TransactionalEmail.RESET_PASSWORD_TO_PRO.value,
        params={
            "LIEN_NOUVEAU_MDP": reinit_password_url,
        },
    )


def send_reset_password_email_to_pro(user: users_models.User, token: users_models.Token) -> bool:
    data = get_reset_password_to_pro_email_data(user, token)
    return mails.send(recipients=[user.email], data=data)


def get_reset_password_link_to_admin_email_data(
    created_user: users_models.User, reset_password_link: str
) -> models.TransactionalWithoutTemplateEmailData:
    return models.TransactionalWithoutTemplateEmailData(
        subject="Création d'un compte pro",
        html_content=(
            "<html><head></head><body>"
            "<div><div>Bonjour,</div>"
            f"<div>Vous venez de créer le compte de {created_user.firstName} {created_user.lastName}.</div>"
            f"<div>Le lien de création de mot de passe est <a href='{reset_password_link}'>{reset_password_link}</a></div>"
        ),
    )


def send_reset_password_link_to_admin_email(
    created_user: users_models.User,
    admin_email: users_models.User,
    reset_password_link: str,
) -> bool:
    data = get_reset_password_link_to_admin_email_data(created_user, reset_password_link)
    return mails.send(recipients=[admin_email], data=data)


def get_reset_password_from_connected_pro_email_data(user: users_models.User) -> models.TransactionalEmailData:
    departmentCode = user.departementCode
    if departmentCode:
        now = utc_datetime_to_department_timezone(datetime.utcnow(), departmentCode)
    else:
        now = utc_datetime_to_department_timezone(datetime.utcnow(), "75")

    return models.TransactionalEmailData(
        template=TransactionalEmail.RESET_PASSWORD_TO_CONNECTED_PRO.value,
        params={
            "EVENT_DATE": get_date_formatted_for_email(now),
            "EVENT_HOUR": get_time_formatted_for_email(now),
        },
    )


def send_reset_password_email_to_connected_pro(user: users_models.User) -> bool:
    # Users can change their password without an email link when
    # they were connected to the app.
    data = get_reset_password_from_connected_pro_email_data(user)
    return mails.send(recipients=[user.email], data=data)
