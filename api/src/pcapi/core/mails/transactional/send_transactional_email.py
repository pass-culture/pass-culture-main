import json
import logging

import brevo_python
from brevo_python.rest import ApiException

from pcapi import settings
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.utils import email as email_utils
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def send_transactional_email(payload: SendTransactionalEmailRequest) -> None:
    to = [{"email": email} for email in payload.recipients]
    bcc = [{"email": email} for email in payload.bcc_recipients] if payload.bcc_recipients else None
    sender = payload.sender
    reply_to = payload.reply_to

    if payload.enable_unsubscribe:
        headers = None
    else:
        headers = {"X-List-Unsub": "disabled"}

    extra = {
        "template_id": payload.template_id,
        "subject": payload.subject,
        "sender": payload.sender,
        "recipients": payload.recipients,
        "reply_to": payload.reply_to,
    }

    send_smtp_email = brevo_python.SendSmtpEmail(to=to, bcc=bcc, sender=sender, reply_to=reply_to, headers=headers)

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
        logger.error("Invalid payload in send_transactional_email", extra=extra)
        return

    try:
        configuration = brevo_python.Configuration()
        if settings.PROXY_CERT_BUNDLE is not None:
            configuration.ssl_ca_cert = settings.PROXY_CERT_BUNDLE
        if payload.use_pro_subaccount:
            configuration.api_key["api-key"] = settings.SENDINBLUE_PRO_API_KEY
        else:
            configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))
        api_instance.send_transac_email(send_smtp_email)

    except ApiException as exception:
        status = int(exception.status) if exception.status else 0
        if status >= 500:
            raise requests.ExternalAPIException(is_retryable=True) from exception

        code = "unknown"
        if exception.body:
            try:
                data = json.loads(exception.body)
                if data.get("code"):
                    code = data["code"]

                if status == 400 and code == "invalid_parameter":
                    # Don't raise exception for data which should be fixed but create a specific alert for every case.
                    # This should avoid aggregation of all recipients in a single Sentry alert, so would help identify
                    # invalid emails and potential other invalid parameters lost in the crowd.
                    logger.error(
                        "Sendinblue can't send email to %s: code=%s, message=%s",
                        # Email is partially obfuscated in logs but full email is available in Sentry for investigation
                        ",".join(email_utils.anonymize_email(recipient) for recipient in payload.recipients),
                        code,
                        data.get("message"),
                        extra={
                            "template_id": payload.template_id,
                            "recipients": payload.recipients,
                            "bcc_recipients": payload.bcc_recipients,
                        },
                    )
                    return
            except json.JSONDecodeError:
                pass

        logger.exception(
            f"Exception when calling Sendinblue send_transac_email with status={exception.status} and code={code}",
            extra=extra,
        )
        raise requests.ExternalAPIException(is_retryable=False) from exception

    except Exception as exception:
        raise requests.ExternalAPIException(is_retryable=True) from exception
