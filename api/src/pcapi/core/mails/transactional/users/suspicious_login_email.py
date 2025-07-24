from datetime import datetime

import pcapi.core.users.models as users_models
from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.urls import generate_app_link


def get_suspicious_login_email_data(
    user: users_models.User,
    login_info: users_models.LoginDeviceHistory | None,
    account_suspension_token: token_utils.Token,
    reset_password_token: token_utils.Token,
) -> models.TransactionalEmailData:
    # We called `create_reset_password_token()` without explicly
    # passing an empty expiration date. The token hence has one.
    assert user.id == reset_password_token.user_id
    expiration_date = reset_password_token.get_expiration_date_from_token()
    assert expiration_date is not None  # helps mypy
    ACCOUNT_SECURING_LINK = generate_app_link(
        path="securisation-compte",
        params={
            "token": account_suspension_token.encoded_token,
            "reset_password_token": reset_password_token.encoded_token,
            "reset_token_expiration_timestamp": int(expiration_date.timestamp()),
            "email": user.email,
        },
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
    user: users_models.User,
    login_info: users_models.LoginDeviceHistory | None,
    account_suspension_token: token_utils.Token,
    reset_password_token: token_utils.Token,
) -> None:
    data = get_suspicious_login_email_data(user, login_info, account_suspension_token, reset_password_token)
    mails.send(recipients=[user.email], data=data)
