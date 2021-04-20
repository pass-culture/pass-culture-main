import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings


logger = logging.getLogger(__name__)


class SendinblueBackend:
    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))

    def send_transactional_sms(self, recipient: str, content: str) -> bool:
        send_transac_sms = sib_api_v3_sdk.SendTransacSms(
            sender="PassCulture",
            recipient=recipient,
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
