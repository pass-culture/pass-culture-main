"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bdalbianco/PC-38127_venueActivity_specific_cases \
  -f NAMESPACE=set_venue_activity_specific_cases \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.app import app
from pcapi.core.criteria.models import Criterion
from pcapi.core.educational.models import EducationalDomain
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)


def set_specific_cases(not_dry: bool) -> None:
    base = (
        db.session.query(Venue)
        .filter(
            Venue.isOpenToPublic.is_(True),
            (Venue.venueTypeCode == "OTHER") | (Venue.venueTypeCode == "DIGITAL"),
            Venue.activity.is_(None) | (Venue.activity == Activity.NOT_ASSIGNED),
        )
        .options(
            sa_orm.joinedload(offerer_models.Venue.criteria).load_only(Criterion.name),
            sa_orm.joinedload(offerer_models.Venue.collectiveDomains).load_only(EducationalDomain.name),
        )
    )

    # Offerer rejeté => OTHER
    # Offerer inactif => OTHER
    rejected_offerers = (
        base.options(
            sa_orm.joinedload(offerer_models.Venue.managingOfferer).load_only(
                offerer_models.Offerer.validationStatus, offerer_models.Offerer.isActive
            )
        )
        .where(
            offerer_models.Venue.managingOfferer.has(
                sa.or_(
                    offerer_models.Offerer.validationStatus == "REJECTED", offerer_models.Offerer.isActive.is_(False)
                )
            )
        )
        .all()
    )
    for venue in rejected_offerers:
        venue.activity = Activity.OTHER

    venues = base.all()

    # Tag “Microfolie” => MUSEUM Tag “Culture scientifique” => SCIENCE_CENTRE Tag “Cinéma d'art et d'essai” => CINEMA
    for venue in venues:
        for criterion in venue.criteria:
            if criterion.name == "Microfolie":
                venue.activity = Activity.MUSEUM
            elif criterion.name == "Culture scientifique":
                venue.activity = Activity.SCIENCE_CENTRE
            elif criterion.name == "Cinéma d'art et d'essai":
                venue.activity = Activity.CINEMA
    left_venues = [x for x in venues if x.activity is None or x.activity == Activity.NOT_ASSIGNED]

    # Domaine EAC “Patrimoine” => HERITAGE_SITE, “Culture scientifique, technique et industrielle” => SCIENCE_CENTRE
    for venue in left_venues:
        for elem in venue.collectiveDomains:
            if elem.name == "Patrimoine":
                venue.activity = Activity.HERITAGE_SITE
                break
            if elem.name == "Culture scientifique, technique et industrielle":
                venue.activity = Activity.SCIENCE_CENTRE
                break


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    try:
        db.session.execute(sa.text("SET SESSION statement_timeout = '300s'"))
        set_specific_cases(not_dry=args.not_dry)
    finally:
        db.session.execute(sa.text(f"SET SESSION statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}"))

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
