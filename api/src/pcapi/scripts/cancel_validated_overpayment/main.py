"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41611-cancel-validated-overpayment \
  -f NAMESPACE=cancel_validated_overpayment \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(incidentId: int) -> None:
    incident = (
        db.session.query(finance_models.FinanceIncident)
        .filter(finance_models.FinanceIncident.id == incidentId)
        .one_or_none()
    )
    if not incident:
        return

    # only one booking_finance_incident (on a collective booking), with only one finance_event, with only one pricing
    collective_booking = incident.booking_finance_incidents[0].collectiveBooking
    if not collective_booking:  # help mypy
        return
    finance_event = incident.booking_finance_incidents[0].finance_events[0]
    pricing = finance_event.pricings[0]

    pricing.status = finance_models.PricingStatus.CANCELLED
    db.session.add(pricing)
    logger.info(
        "Cancelled pricing",
        extra={"event": finance_event.id, "pricing": pricing.id},
    )

    finance_event.status = finance_models.FinanceEventStatus.CANCELLED
    db.session.add(finance_event)
    logger.info(
        "Cancelled finance event and its pricing",
        extra={
            "event": finance_event.id,
            "pricing": pricing.id,
        },
    )

    incident.status = finance_models.IncidentStatus.CANCELLED
    db.session.add(incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CANCELLED,
        author=None,
        finance_incident=incident,
        comment="PC-41611 - Annulation du trop perçu après sa validation",
    )

    collective_booking.status = educational_models.CollectiveBookingStatus.REIMBURSED
    collective_booking.cancellationDate = None
    collective_booking.cancellationReason = None
    # get dateUsed from the finance event of the booking (not the incident)
    collective_booking.dateUsed = collective_booking.finance_events[0].pricingOrderingDate
    db.session.add(collective_booking)
    db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--incident-id", type=int, required=True)
    args = parser.parse_args()

    main(args.incident_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
