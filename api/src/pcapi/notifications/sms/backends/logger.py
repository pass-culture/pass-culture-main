import logging

from pcapi.core.events import backend as events_backend


logger = logging.getLogger(__name__)


class LoggerBackend(events_backend.ExternalServiceBackend):
    def send_transactional_sms(self, recipient: str, content: str) -> bool:
        logger.info(
            "A transactional sms request would be sent to number='%s' with content='%s'.",
            recipient,
            content,
        )
        return True

    def handle_event(self, event: events_backend.Event) -> None:
        logger.info(
            "An event would be tracked with name='%s' and payload='%s'.",
            event.name,
            event.payload,
        )
