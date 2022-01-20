import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest


logger = logging.getLogger(__name__)


def send_transactional_email(payload: SendTransactionalEmailRequest) -> bool:
    to = [{"email": email} for email in payload.recipients]
    #  FIXME(2022-01-20, tgabin): use an env variable
    sender = (
        {"email": settings.SUPPORT_EMAIL_ADDRESS, "name": "pass Culture"}
        if payload.template_id != 364
        else {"email": "support-pro@passculture.app", "name": "pass Culture [PRO]"}
    )
    template_id = payload.template_id
    tags = payload.tags

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, sender=sender, reply_to=sender, template_id=template_id, tags=tags
    )
    if payload.params:  # params cannot be an empty dict in the API
        send_smtp_email.params = payload.params

    try:
        api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        logger.exception(  # pylint: disable=logging-fstring-interpolation
            f"Exception when calling SMTPApi->send_transac_email with status={e.status}",
            extra={"template_id": payload.template_id, "recipients": payload.recipients},
        )
        return False
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(
            "Unknown exception occurred when calling SMTPApi->send_transac_email",
            extra={"template_id": payload.template_id, "recipients": payload.recipients},
        )
        return False
