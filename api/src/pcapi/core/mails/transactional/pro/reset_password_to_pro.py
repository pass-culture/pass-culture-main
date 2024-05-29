from datetime import datetime

from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.models as users_models
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.mailing import build_pc_pro_reset_password_link


def get_reset_password_to_pro_email_data(token: token_utils.Token) -> models.TransactionalEmailData:
    reinit_password_url = build_pc_pro_reset_password_link(token.encoded_token)
    return models.TransactionalEmailData(
        template=TransactionalEmail.RESET_PASSWORD_TO_PRO.value,
        params={
            "LIEN_NOUVEAU_MDP": reinit_password_url,
        },
    )


def send_reset_password_email_to_pro(token: token_utils.Token) -> None:
    user = users_models.User.query.filter_by(id=token.user_id).one()
    data = get_reset_password_to_pro_email_data(token)
    mails.send(recipients=[user.email], data=data)


def get_reset_password_from_connected_pro_email_data(user: users_models.User) -> models.TransactionalEmailData:
    now = utc_datetime_to_department_timezone(datetime.utcnow(), user.departementCode)

    return models.TransactionalEmailData(
        template=TransactionalEmail.RESET_PASSWORD_TO_CONNECTED_PRO.value,
        params={
            "EVENT_DATE": get_date_formatted_for_email(now),
            "EVENT_HOUR": get_time_formatted_for_email(now),
        },
    )


def send_reset_password_email_to_connected_pro(user: users_models.User) -> None:
    # Users can change their password without an email link when
    # they were connected to the app.
    data = get_reset_password_from_connected_pro_email_data(user)
    mails.send(recipients=[user.email], data=data)
