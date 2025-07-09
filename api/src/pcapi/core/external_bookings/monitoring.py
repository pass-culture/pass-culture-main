import logging

from pcapi.core.providers.models import Provider


logger = logging.getLogger(__name__)


def log_provider_timeout(provider: Provider) -> None:
    logger.warning(
        "External booking request timed out",
        extra={"provider_id": provider.id},
        technical_message_id="external_booking_timeout",
    )
