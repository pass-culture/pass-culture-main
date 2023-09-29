import logging

from pcapi import settings
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization.external_api_booking_notification_tasks import ExternalApiBookingNotificationRequest
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class ExternalApiBookingNotificationTaskPayload(BaseModel):
    data: ExternalApiBookingNotificationRequest
    signature: str
    notificationUrl: str


@task(settings.GCP_EXTERNAL_API_BOOKING_NOTIFICATION_QUEUE_NAME, "/external_api/booking_notification")
def external_api_booking_notification_task(payload: ExternalApiBookingNotificationTaskPayload) -> None:
    try:
        response = requests.post(
            payload.notificationUrl,
            json=payload.data.json(),
            hmac=payload.signature,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exception:
        logger.warning(
            "Failed to call provider notification url: %s",
            exception,
            extra={"stock_id": payload.data.stock_id, "booking_creation_date": payload.data.booking_creation_date},
        )
