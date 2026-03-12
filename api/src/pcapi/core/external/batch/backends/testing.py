from pcapi.core.external.batch import serialization
from pcapi.core.external.batch import testing
from pcapi.core.external.batch.backends.batch import BatchAPI
from pcapi.core.external.batch.backends.batch import UserUpdateData
from pcapi.core.external.batch.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def update_user_attributes(
        self, batch_api: BatchAPI, user_id: int, attribute_values: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        super().update_user_attributes(
            batch_api, user_id, attribute_values, can_be_asynchronously_retried=can_be_asynchronously_retried
        )
        testing.requests.append(
            {
                "user_id": user_id,
                "attribute_values": attribute_values,
                "batch_api": batch_api.name,
                "can_be_asynchronously_retried": can_be_asynchronously_retried,
            }
        )

    def update_user_attributes_new(
        self, user_id: int, attribute_values: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        super().update_user_attributes_new(
            user_id, attribute_values, can_be_asynchronously_retried=can_be_asynchronously_retried
        )
        testing.requests.append(
            {
                "user_id": user_id,
                "attribute_values": attribute_values,
                "can_be_asynchronously_retried": can_be_asynchronously_retried,
            }
        )

    def update_users_attributes(
        self, users_data: list[UserUpdateData], can_be_asynchronously_retried: bool = False
    ) -> None:
        super().update_users_attributes(users_data, can_be_asynchronously_retried=can_be_asynchronously_retried)
        testing.requests.append(users_data)

    def send_transactional_notification(
        self,
        notification_data: serialization.TransactionalNotificationData | serialization.TransactionalNotificationDataV2,
        can_be_asynchronously_retried: bool = False,
    ) -> None:
        super().send_transactional_notification(
            notification_data, can_be_asynchronously_retried=can_be_asynchronously_retried
        )
        testing.requests.append(
            {
                "group_id": notification_data.group_id,
                "user_ids": notification_data.user_ids,
                "message": {"title": notification_data.message.title, "body": notification_data.message.body},
                "can_be_asynchronously_retried": can_be_asynchronously_retried,
                **notification_data.extra,
            }
        )

    def delete_user_attributes(self, user_id: int, can_be_asynchronously_retried: bool = False) -> None:
        super().delete_user_attributes(user_id, can_be_asynchronously_retried=can_be_asynchronously_retried)
        testing.requests.append({"user_id": user_id, "can_be_asynchronously_retried": can_be_asynchronously_retried})

    def track_event(
        self, user_id: int, event_name: str, event_payload: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        super().track_event(
            user_id, event_name, event_payload, can_be_asynchronously_retried=can_be_asynchronously_retried
        )
        testing.requests.append(
            {
                "user_id": user_id,
                "event_name": event_name,
                "event_payload": event_payload,
                "can_be_asynchronously_retried": can_be_asynchronously_retried,
            }
        )

    def track_event_bulk(
        self,
        track_event_data: list[serialization.TrackBatchEventRequest] | list[serialization.TrackBatchEventRequestV2],
        can_be_asynchronously_retried: bool = False,
    ) -> None:
        super().track_event_bulk(track_event_data, can_be_asynchronously_retried=can_be_asynchronously_retried)

        payload = [
            {
                "id": str(track_event.user_id),
                "events": [
                    {
                        "name": f"ue.{track_event.event_name.value}",
                        "attributes": track_event.event_payload,
                    }
                ],
            }
            for track_event in track_event_data
        ]

        testing.requests.append(
            {
                "payload": payload,
                "can_be_asynchronously_retried": can_be_asynchronously_retried,
            }
        )
