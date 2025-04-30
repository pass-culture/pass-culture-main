import logging

import brevo_python
from brevo_python.rest import ApiException

from pcapi import settings
from pcapi.core import mails
import pcapi.core.mails.models as mails_models
from pcapi.models import db
from pcapi.utils import requests
from pcapi.utils.email import is_email_whitelisted


logger = logging.getLogger(__name__)


class SendinblueBackend:
    def __init__(self) -> None:
        configuration = brevo_python.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        self.api_instance = brevo_python.TransactionalSMSApi(brevo_python.ApiClient(configuration))

    def send_transactional_sms(self, recipient: str, content: str) -> None:
        send_transac_sms = brevo_python.SendTransacSms(
            sender="PassCulture",
            recipient=self._format_recipient(recipient),
            content=content,
            type="transactional",
            tag="phone-validation",
        )
        try:
            self.api_instance.send_transac_sms(send_transac_sms)

        except ApiException as exception:
            if exception.status and int(exception.status) >= 500:
                logger.warning(
                    "Sendinblue replied with status=%s when sending SMS",
                    exception.status,
                    extra={"recipient": recipient, "content": content},
                )
                raise requests.ExternalAPIException(is_retryable=True) from exception

            logger.exception("Error while sending SMS", extra={"recipient": recipient, "content": content})
            raise requests.ExternalAPIException(is_retryable=False) from exception

        except Exception as exception:
            logger.warning("Exception caught while sending SMS", extra={"recipient": recipient, "content": content})
            raise requests.ExternalAPIException(is_retryable=True) from exception

    def _format_recipient(self, recipient: str) -> str:
        """Sendinblue does not accept phone numbers with a leading '+'"""
        if recipient.startswith("+"):
            return recipient[1:]
        return recipient


class ToDevSendinblueBackend(SendinblueBackend):
    def send_transactional_sms(self, recipient: str, content: str) -> None:
        # No need to import in production
        import sqlalchemy.orm as sa_orm

        from pcapi.core.users import models as users_models

        if recipient in settings.WHITELISTED_SMS_RECIPIENTS:
            super().send_transactional_sms(recipient, content)
            return

        mail_recipient = settings.DEV_EMAIL_ADDRESS
        mail_content = mails_models.TransactionalWithoutTemplateEmailData(
            subject="Code de validation du téléphone",
            html_content=(
                f"<div>Le contenu suivant serait envoyé par sms au numéro {recipient}</div><div>{content}</div></div>"
            ),
            sender=mails_models.TransactionalSender.SUPPORT_PRO,
        )

        try:
            user = db.session.query(users_models.User).filter(users_models.User.phoneNumber == recipient).one_or_none()
        except sa_orm.exc.MultipleResultsFound:
            logger.error("Several user accounts with the same phone number", extra={"phone_number": recipient})
        else:
            # Imported test users are whitelisted (Internal users, Bug Bounty, audit, etc.)
            if user is not None:
                if (user and user.has_test_role) or is_email_whitelisted(recipient):
                    mail_recipient = user.email

        mails.send(recipients=[mail_recipient], data=mail_content)
