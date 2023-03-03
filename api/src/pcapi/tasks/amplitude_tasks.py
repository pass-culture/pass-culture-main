from pcapi import settings
from pcapi.analytics.amplitude.backends.amplitude_connector import AmplitudeEventType
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task
from pcapi.utils.module_loading import import_string


class TrackAmplitudeEventRequest(BaseModel):
    user_id: int
    event_name: AmplitudeEventType
    event_properties: dict | None = None

    class Config:
        arbitrary_types_allowed = True


@task(settings.AMPLITUDE_QUEUE_NAME, "/amplitude/track_event")
def track_event(
    payload: TrackAmplitudeEventRequest,
) -> None:
    backend = import_string(settings.AMPLITUDE_BACKEND)
    user_id = payload.user_id
    event_name = payload.event_name
    event_properties = payload.event_properties

    backend().track_event(
        user_id=user_id,
        event_name=event_name,
        event_properties=event_properties,
    )
