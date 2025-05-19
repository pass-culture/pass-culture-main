import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.token as token_utils
from pcapi import settings
from pcapi.core.users.models import User


def build_pro_link_for_email_change(token: token_utils.Token) -> str:
    return f"{settings.PRO_URL}/email_validation?token={token.encoded_token}"


def send_pro_user_emails_for_email_change(user: User, new_email: str, token: token_utils.Token) -> None:
    transactional_mails.send_pro_information_email_change_email(user, new_email)
    link_to_email_change = build_pro_link_for_email_change(token)
    transactional_mails.send_pro_confirmation_email_change_email(new_email, link_to_email_change)
