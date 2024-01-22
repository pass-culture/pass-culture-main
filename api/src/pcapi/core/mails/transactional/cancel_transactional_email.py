import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def cancel_scheduled_email(message_id: str) -> None:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    try:
        api_instance.delete_scheduled_email_by_id(message_id)
        logger.info("Cancelled scheduled email", extra={"message_id": message_id})

    except ApiException as exception:
        if exception.status and int(exception.status) == 404:
            # Email was already send or cancelled. Nothing we can do here.
            return

        if exception.status and int(exception.status) >= 500:
            raise requests.ExternalAPIException(is_retryable=True) from exception

    except Exception as exception:
        logger.exception(
            "Exception when cancelling scheduled email",
            extra={"message_id": message_id, "exception": exception},
        )
        raise requests.ExternalAPIException(is_retryable=False) from exception
