import logging
import typing

import brevo
from brevo.core import ApiError as BrevoApiError

from pcapi import settings
from pcapi.utils import email as email_utils
from pcapi.utils import requests

from .. import serialization


logger = logging.getLogger(__name__)


def send_transactional_email(payload: serialization.SendTransactionalEmailRequest) -> None:
    email_kwargs: dict[str, typing.Any] = {}

    if payload.recipients:
        email_kwargs["to"] = [brevo.SendTransacEmailRequestToItem(email=email) for email in payload.recipients]

    if payload.bcc_recipients:
        email_kwargs["bcc"] = [brevo.SendTransacEmailRequestBccItem(email=email) for email in payload.bcc_recipients]

    if payload.sender:
        email_kwargs["sender"] = brevo.SendTransacEmailRequestSender(**payload.sender)

    if payload.reply_to:
        email_kwargs["reply_to"] = brevo.SendTransacEmailRequestReplyTo(**payload.reply_to)

    if not payload.enable_unsubscribe:
        email_kwargs["headers"] = {"X-List-Unsub": "disabled"}

    # Can send email with: to, sender, template_id, tags, params

    if payload.template_id:
        email_kwargs["template_id"] = payload.template_id
        if payload.tags:
            email_kwargs["tags"] = payload.tags
        if payload.params:  # params cannot be an empty dict in the API
            email_kwargs["params"] = payload.params

    # Or can send email with: to, sender, subject, html_content, attachment (Can be None)

    elif payload.subject and payload.html_content:
        email_kwargs["subject"] = payload.subject
        email_kwargs["html_content"] = payload.html_content
        if payload.attachment:  # attachment cannot be an empty list in the API
            email_kwargs["attachment"] = [
                brevo.SendTransacEmailRequestAttachmentItem(**attachment) for attachment in payload.attachment
            ]
    else:
        logger.error("Invalid payload in send_transactional_email", extra={"payload": payload.model_dump()})
        return

    try:
        api_key = settings.SENDINBLUE_PRO_API_KEY if payload.use_pro_subaccount else settings.SENDINBLUE_API_KEY
        client = brevo.Brevo(api_key=api_key, timeout=settings.BREVO_REQUEST_TIMEOUT)
        client.transactional_emails.send_transac_email(**email_kwargs)

    except BrevoApiError as exception:
        status = int(exception.status_code) if exception.status_code else 0
        if status >= 500:
            raise requests.ExternalAPIException(is_retryable=True) from exception

        if isinstance(exception.body, dict):
            code = exception.body.get("code", "unknown")

            if status == 400 and code == "invalid_parameter":
                # Don't raise exception for data which should be fixed but create a specific alert for every case.
                # This should avoid aggregation of all recipients in a single Sentry alert, so would help identify
                # invalid emails and potential other invalid parameters lost in the crowd.
                logger.error(
                    "Brevo can't send email to %s: code=%s, message=%s",
                    # Email is partially obfuscated in logs but full email is available in Sentry for investigation
                    ",".join(email_utils.anonymize_email(recipient) for recipient in payload.recipients),
                    code,
                    exception.body.get("message"),
                    extra={
                        "payload": payload.model_dump(),
                        "status_code": exception.status_code,
                        "body": exception.body,
                    },
                )
                return

        logger.exception(
            "Exception when calling Brevo send_transac_email",
            extra={"payload": payload.model_dump(), "status_code": exception.status_code, "body": exception.body},
        )
        raise requests.ExternalAPIException(is_retryable=False) from exception

    except Exception as exception:
        raise requests.ExternalAPIException(is_retryable=True) from exception
