from datetime import datetime

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.models as users_models
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_suspicious_login_email_data(
    user: users_models.User, login_info: users_models.LoginDeviceHistory | None, token: str
) -> models.TransactionalEmailData:
    ACCOUNT_SECURING_LINK = generate_firebase_dynamic_link(
        path="securisation-compte",
        params={"token": token},
    )

    localized_login_datetime = utc_datetime_to_department_timezone(
        login_info.dateCreated if login_info else datetime.utcnow(), user.departementCode
    )

    if login_info:
        params = {
            "LOCATION": login_info.location,
            "LOGIN_DATE": localized_login_datetime.strftime("%d/%m/%Y"),
            "LOGIN_TIME": get_time_formatted_for_email(localized_login_datetime),
            "OS": login_info.os,
            "SOURCE": login_info.source,
            "ACCOUNT_SECURING_LINK": ACCOUNT_SECURING_LINK,
        }
    else:
        params = {
            "LOGIN_DATE": localized_login_datetime.strftime("%d/%m/%Y"),
            "LOGIN_TIME": get_time_formatted_for_email(localized_login_datetime),
            "ACCOUNT_SECURING_LINK": ACCOUNT_SECURING_LINK,
        }

    return models.TransactionalEmailData(
        template=TransactionalEmail.SUSPICIOUS_LOGIN.value,
        params=params,
    )


def send_suspicious_login_email(
    user: users_models.User, login_info: users_models.LoginDeviceHistory | None, token: str
) -> bool:
    data = get_suspicious_login_email_data(user, login_info, token)
    return mails.send(recipients=[user.email], data=data)
