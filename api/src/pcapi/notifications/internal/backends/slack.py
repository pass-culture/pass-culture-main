import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from pcapi import settings


logger = logging.getLogger(__name__)


class SlackBackend:
    def __init__(self):
        self.client = WebClient(token=settings.SLACK_BOT_TOKEN)

    def send_internal_message(self, channel: str, blocks: list[dict], icon_emoji: str):
        try:
            self.client.chat_postMessage(
                blocks=blocks,
                channel=channel,
                icon_emoji=icon_emoji,
            )
        except SlackApiError as exc:
            logger.exception(
                "Une erreur s'est produite lors de l'envoie d'un message slack",
                extra={"error": str(exc), "channel": channel, "blocks": str(blocks)},
            )
