"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=cnormant/pc-41731 \
  -f NAMESPACE=fix_offers_withdrawals_for_some_products \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    NON_EVENT_SUBCATEGORIES = [
        subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if not subcategory.is_event
    ]

    offers_query = db.session.query(Offer).filter(Offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET)

    updated_count = offers_query.filter(
        Offer.withdrawalDetails.is_(None), Offer.subcategoryId.in_(NON_EVENT_SUBCATEGORIES)
    ).update({Offer.withdrawalType: None}, synchronize_session=False)

    db.session.flush()
    logger.info("Successfully updated %s offers", updated_count)

    other_offers_query = offers_query.filter(Offer.withdrawalDetails.is_not(None))
    total_other_offers = other_offers_query.count()

    if total_other_offers:
        other_offers_sneak_peek = other_offers_query.limit(10).all()
        logger.info(
            "Found some physical offers with NO_TICKET and withdrawalDetails",
            extra={
                "total": total_other_offers,
                "extract": {
                    offer.id: {
                        "name": offer.name,
                        "subcategoryId": offer.subcategoryId,
                        "withdrawalType": offer.withdrawalType,
                        "withdrawalDetails": offer.withdrawalDetails,
                    }
                    for offer in other_offers_sneak_peek
                },
            },
        )
    else:
        logger.info("Found no issues, successfully updated %s offers", updated_count)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
