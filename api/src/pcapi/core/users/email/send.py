from datetime import datetime

from pcapi.core.mails.transactional.users.email_address_change import send_confirmation_email_change_email
from pcapi.core.mails.transactional.users.email_address_change import send_information_email_change_email
from pcapi.core.users.models import User
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.repository.user_queries import find_user_by_email
from pcapi.utils.urls import generate_firebase_dynamic_link


def _build_link_for_email_change(current_email: str, new_email: str, expiration_date: datetime) -> str:
    token = encode_jwt_payload({"current_email": current_email, "new_email": new_email}, expiration_date)
    expiration = int(expiration_date.timestamp())

    path = "changement-email"
    params = {"token": token, "expiration_timestamp": expiration}

    return generate_firebase_dynamic_link(path, params)


def send_user_emails_for_email_change(user: User, new_email: str, expiration_date: datetime) -> None:
    user_with_new_email = find_user_by_email(new_email)
    if user_with_new_email:
        return

    send_information_email_change_email(user)
    link_for_email_change = _build_link_for_email_change(user.email, new_email, expiration_date)
    send_confirmation_email_change_email(user, new_email, link_for_email_change)
