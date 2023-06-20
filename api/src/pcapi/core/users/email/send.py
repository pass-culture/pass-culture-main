from datetime import datetime
from urllib.parse import urlencode

from pcapi import settings
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.core.users.utils import encode_jwt_payload


def build_pro_link_for_email_change(current_email: str, new_email: str, user_id: int, expiration_date: datetime) -> str:
    token = encode_jwt_payload(
        {"current_email": current_email, "new_email": new_email, "user_id": user_id}, expiration_date
    )
    expiration = int(expiration_date.timestamp())

    path = "email_validation"
    params = {
        "token": token,
        "expiration_timestamp": expiration,
    }
    return f"{settings.PRO_URL}/{path}?{urlencode(params)}"


def send_pro_user_emails_for_email_change(user: User, new_email: str, expiration_date: datetime) -> bool:
    user_with_new_email = find_user_by_email(new_email)
    if user_with_new_email:
        return True
    success = transactional_mails.send_pro_information_email_change_email(user, new_email)
    link_to_email_change = build_pro_link_for_email_change(user.email, new_email, user.id, expiration_date)
    success &= transactional_mails.send_pro_confirmation_email_change_email(new_email, link_to_email_change)
    return success
