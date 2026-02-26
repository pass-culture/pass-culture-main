import enum
import logging

from pydantic import BaseModel as BaseModelV2

import pcapi.core.bookings.models as bookings_models
import pcapi.core.providers.repository as providers_repository
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.providers.serialization import ExternalEventBookingRequest
from pcapi.local_providers.provider_manager import synchronize_ems_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class CinemaSynchronisationTaskPayload(BaseModelV2):
    venue_provider_id: int


@celery_async_task(
    name="tasks.providers.default.synchronize_cinema_sessions",
    model=CinemaSynchronisationTaskPayload,
)
def synchronize_cinema_sessions_task(payload: CinemaSynchronisationTaskPayload) -> None:
    venue_provider = providers_repository.get_venue_provider_by_id(payload.venue_provider_id)
    if venue_provider.provider.localClass == "EMSStocks":
        synchronize_ems_venue_provider(venue_provider)
    else:
        synchronize_venue_provider(venue_provider)


class BookingAction(str, enum.Enum):
    BOOK = "BOOK"
    CANCEL = "CANCEL"


class ExternalApiBookingNotificationRequest(ExternalEventBookingRequest):
    action: BookingAction

    @classmethod
    def build(cls, booking: bookings_models.Booking, action: BookingAction) -> "ExternalApiBookingNotificationRequest":
        return cls(
            action=action,
            **ExternalEventBookingRequest.build_external_booking(booking.stock, booking, booking.user).model_dump(),
        )


class ExternalApiBookingNotificationTaskPayload(BaseModelV2):
    data: ExternalApiBookingNotificationRequest
    signature: str
    notificationUrl: str


@celery_async_task(
    name="tasks.providers.default.external_api_booking_notification",
    model=ExternalApiBookingNotificationTaskPayload,
    max_per_time_window=1,
    time_window_size=1,
)
def external_api_booking_notification_task(payload: ExternalApiBookingNotificationTaskPayload) -> None:
    try:
        response = requests.post(
            payload.notificationUrl,
            json=payload.data.model_dump_json(),
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
