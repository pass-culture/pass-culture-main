import typing

from pcapi import settings
from pcapi.core.internal_notifications.backends.logger import LoggerBackend
from pcapi.core.internal_notifications.backends.slack import SlackBackend
from pcapi.core.internal_notifications.backends.testing import TestingBackend


type Backend = SlackBackend | LoggerBackend | TestingBackend

BACKEND_BY_KEY: typing.Final[dict[str, type[Backend]]] = {
    "SlackBackend": SlackBackend,
    "LoggerBackend": LoggerBackend,
    "TestingBackend": TestingBackend,
}


def _get_backend() -> Backend:
    return BACKEND_BY_KEY[settings.INTERNAL_NOTIFICATION_BACKEND]()


def send_internal_message(channel: str, blocks: list[dict], icon_emoji: str) -> None:
    """Send a message to pass Culture team's slack

    On dev: no message is sent, the payload is logged.
    The "Full payload:" printed on this log is meant to be paste straight to the Slack's Block-Kit-Builder for preview (https://app.slack.com/block-kit-builder)

    On tests: the message is saved on the "requests" global object like all other outbound backends.
    This "requests" can be inspected to validate the backend was called.

    Args:
        channel: Slack's channel name as a string. Is typically different in EHP than in production.
        blocks: List of message blocks. Possible format can be found on the slack's documentation (https://api.slack.com/reference/block-kit/blocks)
        icon_emoji: emoji name as a string, for example ":rubber-duck:". Can be used to easily identify the origin of the message. Beware that messages from the same bot are sometimes aggregated in a way that a change of emoji is not visible.
    """
    _get_backend().send_internal_message(channel, blocks, icon_emoji)
