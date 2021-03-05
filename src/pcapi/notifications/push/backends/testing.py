from pcapi.notifications.push import testing
from pcapi.notifications.push.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def update_user_attributes(self, user_id: int, attribute_values: dict) -> None:
        super().update_user_attributes(user_id, attribute_values)
        testing.requests.append({"user_id": user_id, "attribute_values": attribute_values})
