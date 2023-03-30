from pcapi.core import mails
from pcapi.utils.mailing import make_suspended_fraudulent_beneficiary_by_ids_notification_email


def send_suspended_fraudulent_users_email(fraudulent_users: dict, nb_cancelled_bookings: int, recipient: str) -> bool:
    email = make_suspended_fraudulent_beneficiary_by_ids_notification_email(fraudulent_users, nb_cancelled_bookings)
    return mails.send(recipients=[recipient], data=email)
