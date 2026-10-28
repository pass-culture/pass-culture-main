"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=cancel_finance_incident \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(incident_id: int) -> None:
    incident = (
        db.session.query(finance_models.FinanceIncident).filter(finance_models.FinanceIncident.id == incident_id).one()
    )
    event = incident.booking_finance_incidents[0].finance_events[0]

    pricing = db.session.query(finance_models.Pricing).filter(finance_models.Pricing.eventId == event.id).one()
    db.session.query(finance_models.PricingLine).filter_by(pricingId=pricing.id).delete(synchronize_session=False)
    db.session.query(finance_models.PricingLog).filter_by(pricingId=pricing.id).delete(synchronize_session=False)
    db.session.delete(pricing)

    event.status = finance_models.FinanceEventStatus.CANCELLED
    db.session.add(event)

    incident.status = finance_models.IncidentStatus.CANCELLED
    db.session.add(incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CANCELLED,
        author=None,
        finance_incident=incident,
        comment="(PC-44355) Annulation du trop-perçu validé, sans désannulation de la réservation",
    )

    db.session.flush()


if __name__ == "__main__":
    from pcapi.app import app

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
