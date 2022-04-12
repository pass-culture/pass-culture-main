import logging

from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize
from pcapi.tasks.zendesk_tasks import UpdateZendeskAttributesRequest
from pcapi.tasks.zendesk_tasks import update_zendesk_attributes_task
from pcapi.validation.routes import zendesk as zendesk_validation


logger = logging.getLogger(__name__)


@public_api.route("/webhooks/zendesk/ticket_notification", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400, 403])
def zendesk_webhook_ticket_notification(body: zendesk_validation.WebhookRequest) -> None:
    logger.info("Zendesk webhook called: %s", body, extra=body.dict())

    update_zendesk_attributes_task.delay(
        UpdateZendeskAttributesRequest(
            is_new_ticket=body.is_new_ticket,
            ticket_id=body.ticket_id,
            zendesk_user_id=body.requester_id,
            email=body.requester_email,
            phone_number=body.requester_phone,
        )
    )
