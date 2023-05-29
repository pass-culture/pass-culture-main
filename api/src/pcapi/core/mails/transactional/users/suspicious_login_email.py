from datetime import datetime

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import LoginDeviceHistory


def get_suspicious_login_email_data(login_info: LoginDeviceHistory | None) -> models.TransactionalEmailData:
    if login_info:
        params = {
            "LOCATION": login_info.location,
            "LOGIN_DATE": login_info.dateCreated.strftime("%d/%m/%Y"),
            "LOGIN_TIME": login_info.dateCreated.strftime("%H:%M"),
            "OS": login_info.os,
            "SOURCE": login_info.source,
        }
    else:
        params = {
            "LOGIN_DATE": datetime.utcnow().strftime("%d/%m/%Y"),
            "LOGIN_TIME": datetime.utcnow().strftime("%H:%M"),
        }

    return models.TransactionalEmailData(
        template=TransactionalEmail.SUSPICIOUS_LOGIN.value,
        params=params,
    )


def send_suspicious_login_email(user_email: str, login_info: LoginDeviceHistory | None) -> bool:
    data = get_suspicious_login_email_data(login_info)
    return mails.send(recipients=[user_email], data=data)
