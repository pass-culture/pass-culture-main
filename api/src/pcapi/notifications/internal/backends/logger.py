import logging


logger = logging.getLogger(__name__)


class LoggerBackend:
    def send_internal_message(self) -> bool:
        logger.info("An internal message would be sent")
        return True
