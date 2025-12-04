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

import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.criteria.models import Criterion
from pcapi.core.educational.models import EducationalDomain
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import db


logger = logging.getLogger(__name__)


def set_specific_cases(not_dry: bool) -> None:
    base = (
        db.session.query(Venue)
        .filter(
            Venue.isOpenToPublic.is_(True),
            (Venue.venueTypeCode == "OTHER") | (Venue.venueTypeCode == "DIGITAL"),
            Venue.activity.is_(None),
        )
        .options(
            sa_orm.joinedload(offerer_models.Venue.criteria).load_only(Criterion.name),
            sa_orm.joinedload(offerer_models.Venue.collectiveDomains).load_only(EducationalDomain.name),
            sa_orm.joinedload(offerer_models.Venue.offers).load_only(Offer.subcategoryId),
        )
    )

    # Offerer rejeté => OTHER
    rejected_offerers = (
        base.options(
            sa_orm.joinedload(offerer_models.Venue.managingOfferer).load_only(offerer_models.Offerer.validationStatus)
        )
        .where(offerer_models.Venue.managingOfferer.has(offerer_models.Offerer.validationStatus == "REJECTED"))
        .all()
    )
    for venue in rejected_offerers:
        venue.activity = Activity.OTHER
    left = [x for x in base.all() if x not in rejected_offerers]

    # Tag “Microfolie” => MUSEUM Tag “Culture scientifique” => SCIENCE_CENTRE Tag “Cinéma d'art et d'essai” => CINEMA
    for venue in left:
        for criterion in venue.criteria:
            if criterion.name == "Microfolie":
                venue.activity = Activity.MUSEUM
            elif criterion.name == "Culture scientifique":
                venue.activity = Activity.SCIENCE_CENTRE
            elif criterion.name == "Cinéma d'art et d'essai":
                venue.activity = Activity.CINEMA
    left = [x for x in left if x.activity is None]

    # Domaine EAC “Patrimoine” => HERITAGE_SITE
    for venue in left:
        for elem in venue.collectiveDomains:
            print(elem.name)
            if elem.name == "Patrimoine":
                venue.activity = Activity.HERITAGE_SITE
                left.remove(venue)
    left = [x for x in left if x.activity is None]

    for venue in left:
        for offer in venue.offers:
            # Offre individuelle de sous-catégorie “SEANCE_CINE” => CINEMA
            if offer.subcategoryId == "SEANCE_CINE":
                venue.activity = Activity.CINEMA
            # Offre individuelle de sous-catégorie “SPECTACLE_REPRESENTATION” => PERFORMANCE_HALL
            elif offer.subcategoryId == "SPECTACLE_REPRESENTATION":
                venue.activity = Activity.PERFORMANCE_HALL
            # Offre individuelle de sous-catégorie “SUPPORT_PHYSIQUE_MUSIQUE_CD”, “SUPPORT_PHYSIQUE_MUSIQUE_VINYLE” => RECORD_STORE
            elif offer.subcategoryId in ["SUPPORT_PHYSIQUE_MUSIQUE_CD", "SUPPORT_PHYSIQUE_MUSIQUE_VINYLE"]:
                venue.activity = Activity.RECORD_STORE
    left = [x for x in left if x.activity is None]


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    set_specific_cases(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
