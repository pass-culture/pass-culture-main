import logging


logger = logging.getLogger(__name__)


class LoggerBackend:
    def send_transactional_sms(self, recipient: str, content: str) -> bool:
        logger.info(
            "A transactional sms request would be sent to number='%s' with content='%s'.",
            recipient,
            content,
        )
        return True
