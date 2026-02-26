import logging


logger = logging.getLogger(__name__)


def log_backoffice_tracking_data(
    event_name: str,
    extra_data: dict | None = None,
) -> None:
    if extra_data is None:
        extra_data = {}

    logger.info(
        event_name,
        extra={"analyticsSource": "backoffice", **extra_data},
        technical_message_id="backoffice_analytics_event",
    )
