import argparse
import logging

import sqlalchemy as sa

# pylint: disable=unused-import
from pcapi.core.bookings import api as bookings_api
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Migrate full validation rules on offerers")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    logger.info("PC-29760 : Starting migration")

    rules = (
        offers_models.OfferValidationRule.query.options(sa.orm.joinedload(offers_models.OfferValidationRule.subRules))
        .filter(offers_models.OfferValidationRule.isActive.is_(True))
        .order_by(offers_models.OfferValidationRule.name)
    ).all()

    for rule in rules:
        if (
            len(rule.subRules) == 1
            and rule.subRules[0].model == offers_models.OfferValidationModel.OFFERER
            and rule.subRules[0].attribute == offers_models.OfferValidationAttribute.ID
        ):
            logger.info("Rule: %s", rule.name)
            offerer_ids = rule.subRules[0].comparated["comparated"]
            logger.info("Offerer ids: %s", offerer_ids)

            offerers = (
                offerers_models.Offerer.query.filter(offerers_models.Offerer.id.in_(offerer_ids))
                .options(
                    sa.orm.load_only(offerers_models.Offerer.id),
                    sa.orm.joinedload(offerers_models.Offerer.confidenceRule),
                )
                .all()
            )

            for offerer in offerers:
                offerers_api.update_fraud_info(
                    offerer,
                    venue=None,
                    author_user=None,
                    confidence_level=offerers_models.OffererConfidenceLevel.MANUAL_REVIEW,
                    comment=f"Migration de la règle : {rule.name}",
                )

            rule.isActive = False
            db.session.add(rule)

    if args.not_dry:
        db.session.commit()
        logger.info("PC-29760 : Migration completed")
    else:
        db.session.rollback()
        logger.info("PC-29760 : Dry run completed")
