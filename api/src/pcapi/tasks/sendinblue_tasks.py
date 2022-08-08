import logging

from pcapi import settings
from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.core.users.external import sendinblue
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.tasks.serialization.sendinblue_tasks import UpdateProAttributesRequest
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest


logger = logging.getLogger(__name__)

SENDINBLUE_CONTACTS_QUEUE_NAME = settings.GCP_SENDINBLUE_CONTACTS_QUEUE_NAME
SENDINBLUE_PRO_QUEUE_NAME = settings.GCP_SENDINBLUE_PRO_QUEUE_NAME
SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME = settings.GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME
SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME = settings.GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME


@task(SENDINBLUE_CONTACTS_QUEUE_NAME, "/sendinblue/update_contact_attributes")  # type: ignore [arg-type]
def update_contact_attributes_task(payload: UpdateSendinblueContactRequest) -> None:
    sendinblue.make_update_request(payload)


@task(SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME, "/sendinblue/send-transactional-email-primary")  # type: ignore [arg-type]
def send_transactional_email_primary_task(payload: SendTransactionalEmailRequest) -> None:
    send_transactional_email(payload)


@task(SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME, "/sendinblue/send-transactional-email-secondary")  # type: ignore [arg-type]
def send_transactional_email_secondary_task(payload: SendTransactionalEmailRequest) -> None:
    send_transactional_email(payload)


# De-duplicate and delay by 15 minutes, to avoid collecting pro attributes and making an update request to Sendinblue
# several times in a short time when a user managing an offerer makes several changes.
#
# Deduplication of Google tasks is based on identical payload in src.pcapi.tasks.cloud_task.enqueue_internal_task,
# but Google documentation tells that "another task with the same name can't be created for ~1hour after the original
# task was [...] executed."
# Reference: https://cloud.google.com/tasks/docs/reference/rest/v2/projects.locations.queues.tasks/create
#
# So time_id parameter in UpdateProAttributesRequest helps to generate different hashes, so different task ids, every
# 15 minutes. Keep delayed_seconds below consistent with time_id generation.
@task(SENDINBLUE_PRO_QUEUE_NAME, "/sendinblue/update_pro_attributes", True, 900)  # type: ignore [arg-type]
def update_pro_attributes_task(payload: UpdateProAttributesRequest) -> None:
    from pcapi.core.users.external import get_pro_attributes
    from pcapi.core.users.external.sendinblue import update_contact_attributes

    # Keep at least to validate/debug on testing environment
    logger.info("update_pro_attributes_task", extra={"email": payload.email, "time_id": payload.time_id})

    attributes = get_pro_attributes(payload.email)
    update_contact_attributes(payload.email, attributes, asynchronous=False)
