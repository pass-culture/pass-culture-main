from dataclasses import asdict
import logging
from typing import Iterable

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException as SendinblueApiException

from pcapi import settings
from pcapi.core.users.repository import find_user_by_email
from pcapi.tasks.sendinblue_tasks import send_transactional_email_primary_task
from pcapi.tasks.sendinblue_tasks import send_transactional_email_secondary_task
import pcapi.tasks.serialization.sendinblue_tasks as serializers
from pcapi.utils.requests import ExternalAPIException

from .. import models
from .base import BaseBackend


logger = logging.getLogger(__name__)


class SendinblueBackend(BaseBackend):
    def __init__(self) -> None:
        super().__init__()
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        self.contacts_api = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

    def send_mail(
        self,
        recipients: Iterable,
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable[str] = None,
    ) -> models.MailResult:
        if isinstance(data, models.TransactionalEmailData):
            payload = serializers.SendTransactionalEmailRequest(
                recipients=list(recipients),
                bcc_recipients=list(bcc_recipients) if bcc_recipients else None,
                template_id=data.template.id,
                params=data.params,
                tags=data.template.tags,
                sender=asdict(data.template.sender.value),
                reply_to=asdict(data.reply_to),  # equal to template sender if reply_to is None
                subject=None,
                html_content=None,
                attachment=None,
            )
            if data.template.use_priority_queue:
                send_transactional_email_primary_task.delay(payload)
            else:
                send_transactional_email_secondary_task.delay(payload)

        elif isinstance(data, models.TransactionalWithoutTemplateEmailData):
            payload = serializers.SendTransactionalEmailRequest(
                recipients=list(recipients),
                bcc_recipients=list(bcc_recipients) if bcc_recipients else None,
                sender=asdict(data.sender.value),
                subject=data.subject,
                html_content=data.html_content,
                attachment=data.attachment,
                reply_to=asdict(data.reply_to),  # equal to sender if reply_to is None
                template_id=None,
                params=None,
                tags=None,
            )
            send_transactional_email_secondary_task.delay(payload)

        else:
            raise ValueError(f"Tried sending an email via sendinblue, but received incorrectly formatted data: {data}")

        return models.MailResult(sent_data=asdict(data), successful=True)

    def create_contact(self, payload: serializers.UpdateSendinblueContactRequest) -> None:
        contact = sib_api_v3_sdk.CreateContact(
            email=payload.email,
            attributes=payload.attributes,
            list_ids=payload.contact_list_ids,
            update_enabled=True,
            email_blacklisted=payload.emailBlacklisted,
        )

        try:
            self.contacts_api.create_contact(contact)

        except SendinblueApiException as exception:
            if exception.status >= 500:
                raise ExternalAPIException(is_retryable=True) from exception

            logger.exception(
                "Exception when calling Sendinblue create_contact API",
                extra={
                    "email": payload.email,
                    "attributes": payload.attributes,
                },
            )
            raise ExternalAPIException(is_retryable=False) from exception

        except Exception as exception:
            raise ExternalAPIException(is_retryable=True) from exception


class ToDevSendinblueBackend(SendinblueBackend):
    def send_mail(
        self,
        recipients: Iterable,
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable[str] = None,
    ) -> models.MailResult:
        whitelisted_recipients = self._get_whitelisted_recipients(recipients)
        whitelisted_bcc_recipients = self._get_whitelisted_recipients(bcc_recipients) if bcc_recipients else []

        recipients = list(whitelisted_recipients) or [settings.DEV_EMAIL_ADDRESS]
        bcc_recipients = list(whitelisted_bcc_recipients)

        return super().send_mail(recipients=recipients, bcc_recipients=bcc_recipients, data=data)

    def _get_whitelisted_recipients(self, recipient_list: Iterable) -> list:
        whitelisted_recipients = set()
        end_to_end_tests_email_address_arr = settings.END_TO_END_TESTS_EMAIL_ADDRESS.split("@")
        for recipient in recipient_list:
            # Imported test users are whitelisted (Internal users, Bug Bounty, audit, etc.)
            user = find_user_by_email(recipient)
            is_e2e_recipient = (
                len(end_to_end_tests_email_address_arr) == 2
                and recipient.startswith(end_to_end_tests_email_address_arr[0])
                and recipient.endswith(f"@{end_to_end_tests_email_address_arr[1]}")
            )
            staging_whitelisted_email_recipients = settings.IS_STAGING and recipient.endswith("@yeswehack.ninja")
            # Only for e2e, when IS_RUNNING_TESTS is true and EMAIL_BACKEND is pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend
            # This override can be seen in pass-culture-app-native/.github/workflows/e2e-*.yml
            e2e_whitelisted_email_recipients = settings.IS_E2E_TESTS and is_e2e_recipient
            if (
                (user and user.has_test_role)
                or recipient in settings.WHITELISTED_EMAIL_RECIPIENTS
                or staging_whitelisted_email_recipients
                or e2e_whitelisted_email_recipients
            ):
                whitelisted_recipients.add(recipient)
        return list(whitelisted_recipients)
