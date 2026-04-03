"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-40500-switch-accurate-venues-to-permanent \
  -f NAMESPACE=switch_venue_to_permanent \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def main(commit: bool) -> None:
    if not commit:
        mark_transaction_as_invalid()

    venues_to_update = (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.isSoftDeleted.is_(False),
            offerers_models.Venue.isPermanent.is_(False),
            sa.or_(
                offerers_models.Venue.siret.isnot(None),
                offerers_models.Venue.isOpenToPublic.is_(True),
            ),
        )
        .all()
    )

    updated_ids = []
    for venue in venues_to_update:
        try:
            with atomic():
                venue.isPermanent = True
                db.session.flush()
                updated_ids.append(venue.id)

        except Exception as e:
            logger.warning(f"Erreur lors de l'update de la Venue {venue.id}: {e}")
            continue

    logger.info(f"Mis à jour de: {len(updated_ids)} venues")
    logger.info(f"Echec de: {len(venues_to_update) - len(updated_ids)} venues")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    main(commit=args.commit)

    if not args.commit:
        logger.info("Dry run terminé, rollback des données")
    else:
        logger.info("Script terminé avec succès")
