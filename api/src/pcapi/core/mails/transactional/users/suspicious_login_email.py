from datetime import datetime

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import LoginDeviceHistory
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_suspicious_login_email_data(login_info: LoginDeviceHistory | None, token: str) -> models.TransactionalEmailData:
    ACCOUNT_SECURING_LINK = generate_firebase_dynamic_link(
        path="securisation-compte",
        params={"token": token},
    )

    if login_info:
        params = {
            "LOCATION": login_info.location,
            "LOGIN_DATE": login_info.dateCreated.strftime("%d/%m/%Y"),
            "LOGIN_TIME": get_time_formatted_for_email(login_info.dateCreated),
            "OS": login_info.os,
            "SOURCE": login_info.source,
            "ACCOUNT_SECURING_LINK": ACCOUNT_SECURING_LINK,
        }
    else:
        params = {
            "LOGIN_DATE": datetime.utcnow().strftime("%d/%m/%Y"),
            "LOGIN_TIME": get_time_formatted_for_email(datetime.utcnow()),
            "ACCOUNT_SECURING_LINK": ACCOUNT_SECURING_LINK,
        }

    return models.TransactionalEmailData(
        template=TransactionalEmail.SUSPICIOUS_LOGIN.value,
        params=params,
    )


def send_suspicious_login_email(user_email: str, login_info: LoginDeviceHistory | None, token: str) -> bool:
    data = get_suspicious_login_email_data(login_info, token)
    return mails.send(recipients=[user_email], data=data)
