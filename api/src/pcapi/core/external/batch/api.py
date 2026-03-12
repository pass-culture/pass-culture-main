import typing

from pcapi import settings
from pcapi.core.external.batch.backends.batch import BatchAPI
from pcapi.core.external.batch.backends.batch import BatchBackend
from pcapi.core.external.batch.backends.batch import UserUpdateData
from pcapi.core.external.batch.backends.logger import LoggerBackend
from pcapi.core.external.batch.backends.testing import TestingBackend
from pcapi.core.external.batch.models import BatchEvent
from pcapi.core.external.batch.serialization import TrackBatchEventRequest
from pcapi.core.external.batch.serialization import TransactionalNotificationData
from pcapi.core.external.batch.serialization import TransactionalNotificationDataV2


type Backend = BatchBackend | LoggerBackend | TestingBackend

BACKEND_BY_KEY: typing.Final[dict[str, type[Backend]]] = {
    "BatchBackend": BatchBackend,
    "LoggerBackend": LoggerBackend,
    "TestingBackend": TestingBackend,
}


def _get_backend() -> Backend:
    return BACKEND_BY_KEY[settings.PUSH_NOTIFICATION_BACKEND]()


def update_user_attributes(
    batch_api: BatchAPI, user_id: int, attribute_values: dict, can_be_asynchronously_retried: bool = False
) -> None:
    return _get_backend().update_user_attributes(
        batch_api, user_id, attribute_values, can_be_asynchronously_retried=can_be_asynchronously_retried
    )


def update_users_attributes(users_data: list[UserUpdateData], can_be_asynchronously_retried: bool = False) -> None:
    _get_backend().update_users_attributes(users_data, can_be_asynchronously_retried=can_be_asynchronously_retried)


def send_transactional_notification(
    notification_data: TransactionalNotificationData | TransactionalNotificationDataV2,
    can_be_asynchronously_retried: bool = False,
) -> None:
    _get_backend().send_transactional_notification(
        notification_data, can_be_asynchronously_retried=can_be_asynchronously_retried
    )


def delete_user_attributes(user_id: int, can_be_asynchronously_retried: bool = False) -> None:
    _get_backend().delete_user_attributes(user_id, can_be_asynchronously_retried=can_be_asynchronously_retried)


def track_event(
    user_id: int, event: BatchEvent, event_payload: dict, can_be_asynchronously_retried: bool = False
) -> None:
    _get_backend().track_event(
        user_id, event.value, event_payload, can_be_asynchronously_retried=can_be_asynchronously_retried
    )


def track_event_bulk(
    track_event_data: list[TrackBatchEventRequest], can_be_asynchronously_retried: bool = False
) -> None:
    _get_backend().track_event_bulk(track_event_data, can_be_asynchronously_retried=can_be_asynchronously_retried)
