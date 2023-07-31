import logging

from pcapi.core.finance import factories as finance_factories


logger = logging.getLogger(__name__)


def create_industrial_incidents() -> None:
    incidents = finance_factories.FinanceIncidentFactory.create_batch(10)
    booking_incidents = []
    for incident in incidents:
        booking_incidents += finance_factories.IndividualBookingFinanceIncidentFactory.create_batch(
            3, incident=incident
        )

    logger.info("created %d incidents", len(incidents))
    logger.info("created %d booking_incidents", len(booking_incidents))
