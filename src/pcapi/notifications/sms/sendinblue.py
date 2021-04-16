import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings


logger = logging.getLogger(__name__)

# TODO: add abstract classes like with Mailjet api when we are certain to go with Sendinblue


class SendinblueBackend:
    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))

    def send_transac_sms(self, content: str, recipient: str) -> None:
        send_transac_sms = sib_api_v3_sdk.SendTransacSms(
            sender="PassCulture",
            recipient=recipient,
            content=content,
            type="transactional",
            tag="phone-validation",
        )
        try:
            api_response = self.api_instance.send_transac_sms(send_transac_sms)
            return api_response.ok

        except ApiException as e:
            logger.exception("Exception when calling TransactionalSMSApi->send_transac_sms: %s\n", e)
            return False
