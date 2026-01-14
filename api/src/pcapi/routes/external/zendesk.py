import logging

from pcapi.connectors.serialization import zendesk_serializers
from pcapi.core.external.zendesk import tasks
from pcapi.core.external.zendesk.serialization import UpdateZendeskAttributesRequest
from pcapi.core.external.zendesk.serialization import ZendeskCheckUpdateRequestStatus
from pcapi.models.feature import FeatureToggle
from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize
from pcapi.tasks import zendesk_tasks as gcp_tasks


logger = logging.getLogger(__name__)


@public_api.route("/webhooks/zendesk/ticket_notification", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400, 403])
def zendesk_webhook_ticket_notification(body: zendesk_serializers.WebhookRequest) -> None:
    anonymized_body = {
        "is_new_ticket": body.is_new_ticket,
        "requester_id": body.requester_id,
        "ticket_id": body.ticket_id,
    }
    logger.info("Zendesk webhook called: %s", anonymized_body, extra=anonymized_body)

    data = UpdateZendeskAttributesRequest(
        is_new_ticket=body.is_new_ticket,
        ticket_id=int(body.ticket_id),
        zendesk_user_id=int(body.requester_id),
        email=body.requester_email,
        phone_number=body.requester_phone,
    )

    if FeatureToggle.WIP_ASYNCHRONOUS_CELERY_ZENDESK.is_active():
        tasks.update_zendesk_attributes_task.delay(data.dict())
    else:
        gcp_tasks.update_zendesk_attributes_task.delay(data)


@public_api.route("/webhooks/zendesk/update-request-status", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400, 403])
def zendesk_update_request_status(body: zendesk_serializers.WebhookFormRequest) -> None:
    anonymized_body = {k: v for k, v in dict(body).items() if k != "requester_email"}
    logger.info("Zendesk webhook called: %s", anonymized_body, extra=anonymized_body)
    logger.info(body.requester_email)

    if "rouzet" not in body.requester_email:  # TODO: this is for debug only
        return

    data = ZendeskCheckUpdateRequestStatus(
        ticket_id=int(body.ticket_id),
        zendesk_user_id=int(body.requester_id),
        email=body.requester_email,
        first_name=body.first_name,
        dossier_dn=body.dossier_dn,
    )

    tasks.check_update_request_status_task.delay(data.dict())
