import json
import logging


logger = logging.getLogger(__name__)


class LoggerBackend:
    def send_internal_message(self, channel: str, blocks, icon_emoji: str):
        logger.info(
            "An internal message would be sent to channel %s with icon %s. Full payload: %s",
            channel,
            icon_emoji,
            json.dumps({"blocks": blocks}),
        )
