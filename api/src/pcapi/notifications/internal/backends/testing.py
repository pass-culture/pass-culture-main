from pcapi.notifications.internal import testing
from pcapi.notifications.internal.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def send_internal_message(self, channel: str, blocks: list[dict], icon_emoji: str):  # type: ignore [no-untyped-def]
        super().send_internal_message(channel, blocks, icon_emoji)
        testing.requests.append({"channel": channel, "blocks": blocks, "icon_emoji": icon_emoji})
