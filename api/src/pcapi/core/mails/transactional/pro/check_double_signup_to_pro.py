from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.utils import date as date_utils
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.mailing import build_pc_pro_reset_password_link


def get_double_signup_to_pro_email_data(user: User, token: token_utils.Token) -> models.TransactionalEmailData:
    reset_password_url = build_pc_pro_reset_password_link(token.encoded_token)

    now = utc_datetime_to_department_timezone(date_utils.get_naive_utc_now(), user.departementCode)
    date = get_date_formatted_for_email(now)
    hour = get_time_formatted_for_email(now)

    return models.TransactionalEmailData(
        template=TransactionalEmail.CHECK_DOUBLE_SIGNUP_TO_PRO.value,
        params={
            "DATE": date,
            "HOUR": hour,
            "LIEN_NOUVEAU_MDP": reset_password_url,
        },
    )


def send_double_signup_to_pro_email(user: User, token: token_utils.Token) -> None:
    data = get_double_signup_to_pro_email_data(user, token)
    mails.send(recipients=[user.email], data=data)
