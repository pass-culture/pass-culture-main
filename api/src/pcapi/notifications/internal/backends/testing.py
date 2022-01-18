from pcapi.notifications.internal import testing
from pcapi.notifications.internal.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def send_internal_message(self) -> bool:
        super().send_internal_message()
        testing.requests.append({})
        return True
