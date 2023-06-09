import datetime

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.repository as users_repository


def send_wake_up_after_inactivity_to_pros() -> None:
    fourty_days_ago = datetime.date.today() - datetime.timedelta(days=40)

    email_data_tuples = users_repository.get_emails_without_active_offers(fourty_days_ago)
    mail_params_by_email = _aggregate_duplicate_mails(email_data_tuples)
    recipients_by_param_tuple = _group_by_mail_params(mail_params_by_email)

    for (can_last_offer_expire, is_last_offer_event), recipients in recipients_by_param_tuple.items():
        mails.send(
            recipients=recipients,
            data=models.TransactionalEmailData(
                template=TransactionalEmail.WAKE_UP_AFTER_INACTIVITY.value,
                params={"CAN_EXPIRE": can_last_offer_expire, "IS_EVENT": is_last_offer_event},
            ),
        )


def _aggregate_duplicate_mails(email_data_tuples: list[tuple[str, bool, bool]]) -> dict[str, dict[str, bool]]:
    mail_params_by_email = {}
    for email, can_last_offer_expire, is_last_offer_event in email_data_tuples:
        if email not in mail_params_by_email:
            mail_params_by_email[email] = {"CAN_EXPIRE": False, "IS_EVENT": False}
        mail_params = mail_params_by_email[email]
        mail_params_by_email[email] = {
            "CAN_EXPIRE": mail_params["CAN_EXPIRE"] or can_last_offer_expire,
            "IS_EVENT": mail_params["IS_EVENT"] or is_last_offer_event,
        }
    return mail_params_by_email


def _group_by_mail_params(mail_params_by_email: dict[str, dict[str, bool]]) -> dict[tuple[bool, bool], list[str]]:
    recipients_by_param_tuple: dict[tuple[bool, bool], list[str]] = {}
    for email, mail_params in mail_params_by_email.items():
        param_tuple = (mail_params["CAN_EXPIRE"], mail_params["IS_EVENT"])
        if param_tuple not in recipients_by_param_tuple:
            recipients_by_param_tuple[param_tuple] = []
        recipients_by_param_tuple[param_tuple].append(email)
    return recipients_by_param_tuple
