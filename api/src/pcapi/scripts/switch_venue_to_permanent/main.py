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


logger = logging.getLogger(__name__)


def main(commit: bool) -> None:
    db.session.execute(
        sa.update(offerers_models.Venue)
        .where(
            offerers_models.Venue.isSoftDeleted.is_(False),
            offerers_models.Venue.isPermanent.is_(False),
            sa.or_(
                offerers_models.Venue.siret.isnot(None),
                offerers_models.Venue.isOpenToPublic.is_(True),
            ),
        )
        .values(isPermanent=True)
        .execution_options(synchronize_session=False)
    )
    try:
        db.session.flush()
    except Exception as e:
        logger.warning(f"Erreur durant le flush {e}")

    if not commit:
        db.session.rollback()
        logger.info("Dry run terminé, rollback des données")
    else:
        db.session.commit()
        logger.info("Script terminé avec succès")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    main(commit=args.commit)
