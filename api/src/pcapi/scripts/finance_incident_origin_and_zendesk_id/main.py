import argparse
import logging
import re

from pcapi.core.finance import models as finance_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def add_zendesk_id_and_origin_to_finance_incident(do_update: bool) -> None:
    logger.info("[FINANCE INCIDENT][START]")

    finance_incidents = finance_models.FinanceIncident.query.all()
    for incident in finance_incidents:
        comment = incident.details.get("origin", "").lower()
        if comment:

            # ORIGIN PART
            if "fraude" in comment or "fraue" in comment:
                incident.origin = finance_models.FinanceIncidentRequestOrigin.FRAUDE
                logger.info(
                    "[FINANCE INCIDENT][UPDATE ORIGIN] Incident ID: %d, origin %s", incident.id, incident.origin
                )
            elif "jeune" in comment:
                incident.origin = finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE
                logger.info(
                    "[FINANCE INCIDENT][UPDATE ORIGIN] Incident ID: %d, origin %s", incident.id, incident.origin
                )
            elif "pro" in comment:
                incident.origin = finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO
                logger.info(
                    "[FINANCE INCIDENT][UPDATE ORIGIN] Incident ID: %d, origin %s", incident.id, incident.origin
                )
            else:
                author_id = incident.details["authorId"]
                if author_id == 1388409:
                    incident.origin = finance_models.FinanceIncidentRequestOrigin.FRAUDE
                    logger.info(
                        "[FINANCE INCIDENT][UPDATE ORIGIN] Incident ID: %d, origin %s", incident.id, incident.origin
                    )
                elif author_id in [3807624, 1531494, 2262518, 5891641, 3811487, 7323646]:
                    incident.origin = finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO
                    logger.info(
                        "[FINANCE INCIDENT][UPDATE ORIGIN] Incident ID: %d, origin %s", incident.id, incident.origin
                    )
                else:
                    logger.info("[FINANCE INCIDENT][UPDATE ORIGIN] Incident ID: %d NOT ORIGIN FOUND", incident.id)

            # ZENDESK PART
            if "#" in comment:
                zendesk_search = re.search(r"#(\d*)", comment, re.IGNORECASE)
                if zendesk_search and zendesk_search.group(1):
                    incident.zendeskId = int(zendesk_search.group(1))
                    logger.info(
                        "[FINANCE INCIDENT][ADD ZENDESK ID] Incident ID: %d, zendeskId %d",
                        incident.id,
                        incident.zendeskId,
                    )

            elif "https://passculture.zendesk.com/agent/tickets/" in comment:
                incident.zendeskId = int(comment.split("/")[-1])
                logger.info(
                    "[FINANCE INCIDENT][ADD ZENDESK ID] Incident ID: %d, zendeskId %d",
                    incident.id,
                    incident.zendeskId,
                )

            # Suppression du champs
            if "origin" in incident.details:
                del incident.details["origin"]

    logger.info("[FINANCE INCIDENT][END]")

    if do_update:
        db.session.commit()
    else:
        db.session.rollback()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Fill fields zendesk id and origin from finance incident table")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    add_zendesk_id_and_origin_to_finance_incident(do_update=args.not_dry)
