import datetime
import logging
import typing

from flask import current_app as app
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings
from pcapi.core.bookings import constants as bookings_constants
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def save_message_ids_for_scheduled_emails(response: typing.Any, payload: SendTransactionalEmailRequest) -> None:
    # transactional email scheduled response code is 202. Doc: https://developers.brevo.com/reference/sendtransacemail
    if response and response.status_code == 202:
        # find message ids in response
        message_id = response.json().get("messageId", None)

        if not message_id:
            return

        data = payload.params or {}
        scheduled_at = payload.scheduled_at
        if scheduled_at is None:
            logger.error("The email was scheduled by the mail provider, but no param `scheduled_at` found in response")
            return

        # If the data contains a BOOKING_ID, we save the message ids in redis
        # so that we can retrieve them later to cancel the scheduled email if the stock changes, or the booking is cancelled
        if "BOOKING_ID" in data:
            suffix = bookings_constants.REDIS_SCHEDULED_EMAILS_SUFFIX
            booking_id = data["BOOKING_ID"]
            app.redis_client.set(f"{booking_id}{suffix}", message_id, ex=(scheduled_at - datetime.datetime.utcnow()))
        else:
            message = (
                "Did not save message_ids for scheduled email. "
                "You may want to add a condition to the `save_message_ids_for_scheduled_emails` function "
                "to handle scheduled email cancellation"
            )
            logger.warning(message, extra={"email_template": payload.template_id})


def send_transactional_email(payload: SendTransactionalEmailRequest) -> None:
    to = [{"email": email} for email in payload.recipients]
    bcc = [{"email": email} for email in payload.bcc_recipients] if payload.bcc_recipients else None
    sender = payload.sender
    reply_to = payload.reply_to

    extra = {
        "template_id": payload.template_id,
        "subject": payload.subject,
        "sender": payload.sender,
        "recipients": payload.recipients,
        "reply_to": payload.reply_to,
    }

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, bcc=bcc, sender=sender, reply_to=reply_to)

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

    if payload.scheduled_at:
        send_smtp_email.scheduled_at = payload.scheduled_at.isoformat()

    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        response = api_instance.send_transac_email(send_smtp_email)
        save_message_ids_for_scheduled_emails(response, payload=payload)

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
