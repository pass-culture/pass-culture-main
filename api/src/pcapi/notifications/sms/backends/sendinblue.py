import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData


logger = logging.getLogger(__name__)


class SendinblueBackend:
    def __init__(self):  # type: ignore [no-untyped-def]
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))

    def send_transactional_sms(self, recipient: str, content: str) -> bool:
        send_transac_sms = sib_api_v3_sdk.SendTransacSms(
            sender="PassCulture",
            recipient=self._format_recipient(recipient),
            content=content,
            type="transactional",
            tag="phone-validation",
        )
        try:
            self.api_instance.send_transac_sms(send_transac_sms)
            return True

        except ApiException as e:
            logger.exception("Exception when calling TransactionalSMSApi->send_transac_sms: %s\n", e)
            return False

    def _format_recipient(self, recipient: str):  # type: ignore [no-untyped-def]
        """Sendinblue does not accept phone numbers with a leading '+'"""
        if recipient.startswith("+"):
            return recipient[1:]
        return recipient


class ToDevSendinblueBackend(SendinblueBackend):
    def send_transactional_sms(self, recipient: str, content: str) -> bool:
        if recipient in settings.WHITELISTED_SMS_RECIPIENTS:
            if not super().send_transactional_sms(recipient, content):
                return False

        mail_content = SendinblueTransactionalWithoutTemplateEmailData(
            subject="Code de validation du téléphone",
            html_content=(
                f"<div>Le contenu suivant serait envoyé par sms au numéro {recipient}</div>"
                f"<div>{content}</div></div>"
            ),
        )

        return mails.send(recipients=[settings.DEV_EMAIL_ADDRESS], data=mail_content)
