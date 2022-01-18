from pcapi.notifications.internal import testing
from pcapi.notifications.internal.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def send_internal_message(self, channel: str, blocks, icon_emoji: str):
        super().send_internal_message(channel, blocks, icon_emoji)
        testing.requests.append({"channel": channel, "blocks": blocks, "icon_emoji": icon_emoji})
