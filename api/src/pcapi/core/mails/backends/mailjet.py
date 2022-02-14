import logging
from typing import Iterable

import mailjet_rest

from pcapi import settings

from ..models.models import MailResult
from .base import BaseBackend


logger = logging.getLogger(__name__)


def monkey_patch_mailjet_requests():
    # We want the `mailjet_rest` library to use our wrapper around
    # `requests` to have automatic logging.
    import mailjet_rest.client  # pylint: disable=redefined-outer-name

    import pcapi.utils.requests

    mailjet_rest.client.requests = pcapi.utils.requests


monkey_patch_mailjet_requests()


def _add_template_debugging(message_data: dict) -> None:
    message_data["MJ-TemplateErrorReporting"] = settings.DEV_EMAIL_ADDRESS


class MailjetBackend(BaseBackend):
    def __init__(self):
        super().__init__()
        auth = (settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET)
        self.mailjet_client = mailjet_rest.Client(
            auth=auth,
            version="v3",
            # The mailjet_rest package used `api.eu.mailjet.com` until
            # version 1.3.3, but the SSL certificate expires on
            # 2022-02-20, leading us to think that we should use
            # another domain instead.
            api_url="https://api.mailjet.com/",
        )

    def _send(self, recipients: Iterable[str], data: dict) -> MailResult:
        data["To"] = ", ".join(recipients)

        if settings.MAILJET_TEMPLATE_DEBUGGING:
            messages_data = data.get("Messages")
            if messages_data:
                for message_data in messages_data:
                    _add_template_debugging(message_data)
            else:
                _add_template_debugging(data)

        try:
            response = self.mailjet_client.send.create(data=data, timeout=settings.MAILJET_HTTP_TIMEOUT)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error trying to send e-mail with Mailjet: %s", exc)
            return MailResult(
                sent_data=data,
                successful=False,
            )

        successful = response.status_code == 200
        if not successful:
            logger.warning("Got %d return code from Mailjet: content=%s", response.status_code, response.content)

        return MailResult(
            sent_data=data,
            successful=successful,
        )


class ToDevMailjetBackend(MailjetBackend):
    """A backend where the recipients are overriden.

    This is the backend that should be used on testing and staging
    environments.
    """

    def _inject_html_test_notice(self, recipients, data):
        if "Html-part" not in data:
            return
        notice = (
            f"<p>This is a test (ENV={settings.ENV}). "
            f"In production, this email would have been sent to {', '.join(recipients)}</p>"
        )
        data["Html-part"] = notice + data["Html-part"]

    def send_mail(self, recipients: Iterable[str], data: dict) -> MailResult:
        # FIXME (apibrac, 2021-03-17): we can delete this as soon as AppNative's beta test is finished
        # WHITELISTED_EMAIL_RECIPIENTS should be deleted as well
        some_recipients_are_whitelisted = set(recipients) & set(settings.WHITELISTED_EMAIL_RECIPIENTS)
        if some_recipients_are_whitelisted:
            return super().send_mail(recipients=recipients, data=data)

        self._inject_html_test_notice(recipients, data)
        recipients = [settings.DEV_EMAIL_ADDRESS]
        return super().send_mail(recipients=recipients, data=data)
