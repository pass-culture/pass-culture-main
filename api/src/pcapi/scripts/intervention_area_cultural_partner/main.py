import argparse
import logging

from sqlalchemy import func
from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerer_models
from pcapi.models import db


logger = logging.getLogger(__name__)

LABEL_TO_REMOVE = "culturalPartner"

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    collective_offers: "sa_orm.Query[educational_models.CollectiveOffer]" = db.session.query(
        educational_models.CollectiveOffer
    ).filter(func.cardinality(educational_models.CollectiveOffer.interventionArea) > 0)

    collective_offer_templates: "sa_orm.Query[educational_models.CollectiveOfferTemplate]" = db.session.query(
        educational_models.CollectiveOfferTemplate
    ).filter(func.cardinality(educational_models.CollectiveOfferTemplate.interventionArea) > 0)

    venues: "sa_orm.Query[offerer_models.Venue]" = db.session.query(offerer_models.Venue).filter(
        func.jsonb_array_length(offerer_models.Venue.collectiveInterventionArea) > 0
    )

    fix_count = 0
    for collective_offer in collective_offers.yield_per(1000):
        if LABEL_TO_REMOVE in collective_offer.interventionArea:
            collective_offer.interventionArea = [
                option for option in collective_offer.interventionArea if option != LABEL_TO_REMOVE
            ]
            fix_count += 1

    logger.info("Fixed %s collective offers with invalid interventionArea", fix_count)

    fix_template_count = 0
    for collective_offer_template in collective_offer_templates.yield_per(1000):
        if LABEL_TO_REMOVE in collective_offer_template.interventionArea:
            collective_offer_template.interventionArea = [
                option for option in collective_offer_template.interventionArea if option != LABEL_TO_REMOVE
            ]
            fix_template_count += 1

    logger.info("Fixed %s collective offer templates with invalid interventionArea", fix_template_count)

    fix_venue_count = 0
    for venue in venues.yield_per(1000):
        if venue.collectiveInterventionArea is not None and LABEL_TO_REMOVE in venue.collectiveInterventionArea:
            venue.collectiveInterventionArea = [
                option for option in venue.collectiveInterventionArea if option != LABEL_TO_REMOVE
            ]
            fix_venue_count += 1

    logger.info("Fixed %s venues with invalid collectiveInterventionArea", fix_venue_count)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
