import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def send_transactional_email(payload: SendTransactionalEmailRequest) -> bool:
    to = [{"email": email} for email in payload.recipients]
    sender = payload.sender
    reply_to = payload.reply_to

    extra = {
        "template_id": payload.template_id,
        "subject": payload.subject,
        "sender": payload.sender,
        "recipients": payload.recipients,
        "reply_to": payload.reply_to,
    }

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, sender=sender, reply_to=reply_to)

    # Can send email with: to, sender, template_id, tags, params

    if payload.template_id:
        send_smtp_email.template_id = payload.template_id
        if payload.tags:
            send_smtp_email.tags = payload.tags
        if payload.params:  # params cannot be an empty dict in the API
            send_smtp_email.params = payload.params

    # Or can send email with: to, sender, subject, html_content, attachment (Can be None)

    elif payload.subject and payload.html_content:
        send_smtp_email.subject = payload.subject
        send_smtp_email.html_content = payload.html_content
        if payload.attachment:  # attachment cannot be an empty list in the API
            send_smtp_email.attachment = [
                {"content": attachment.content, "name": attachment.name} for attachment in payload.attachment
            ]
    else:
        logger.exception("Unvalid payload in send_transactional_email", extra=extra)
        return False

    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        api_instance.send_transac_email(send_smtp_email)

    except ApiException as exception:
        if exception.status and int(exception.status) >= 500:
            raise requests.ExternalAPIException(is_retryable=True) from exception

        code = "unknown"
        if exception.body and not isinstance(exception.body, str) and exception.body.get("code"):
            code = exception.body.get("code")
        logger.exception(  # pylint: disable=logging-fstring-interpolation
            f"Exception when calling Sendinblue send_transac_email with status={exception.status} and code={code}",
            extra=extra,
        )
        raise requests.ExternalAPIException(is_retryable=False) from exception

    except Exception as exception:
        raise requests.ExternalAPIException(is_retryable=True) from exception

    return True
