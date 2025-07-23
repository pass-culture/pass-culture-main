import logging

from pcapi.app import app
from pcapi.repository import transaction
from pcapi.workers.update_all_offers_active_status_job import update_venue_synchronized_offers_active_status_job


logger = logging.getLogger(__name__)


def deactivate_closed_venue_offers() -> None:
    venue_provider_pairs_to_deactivate = [
        {"venueId": 13954, "providerId": 2123},  # Decitre V2
        {"venueId": 48372, "providerId": 2123},
        {"venueId": 13954, "providerId": 66},  # Decitre V1
        {"venueId": 48372, "providerId": 66},
    ]

    for pair in venue_provider_pairs_to_deactivate:
        with transaction():
            update_venue_synchronized_offers_active_status_job(
                venue_id=pair["venueId"], provider_id=pair["providerId"], is_active=False
            )
            logger.info("Offers deactivated", extra=pair)


if __name__ == "__main__":
    app.app_context().push()
    deactivate_closed_venue_offers()
