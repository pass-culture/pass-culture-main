"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-38588-end-vbal-vppl-venue-soft-deleted \
  -f NAMESPACE=end_vbal_vppl_venue_soft_deleted \
  -f SCRIPT_ARGUMENTS="--author-id 123";

"""

import argparse
import logging

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def main(author: users_models.User, not_dry: bool = False) -> None:
    if not not_dry:
        logger.info("Script has been run dry, will be rollbacked")
        mark_transaction_as_invalid()

    soft_deleted_venues = (
        db.session.query(offerers_models.Venue)
        .execution_options(include_deleted=True)
        .options(
            sa_orm.selectinload(offerers_models.Venue.bankAccountLinks),
            sa_orm.selectinload(offerers_models.Venue.pricing_point_links),
        )
        .filter(offerers_models.Venue.isSoftDeleted.is_(True))
    ).all()

    now = date_utils.get_naive_utc_now()
    for venue in soft_deleted_venues:
        if venue_bank_account_link := venue.current_bank_account_link:
            venue_bank_account_link.timespan = db_utils.make_timerange(venue_bank_account_link.timespan.lower, now)
            action_history = history_models.ActionHistory(
                venueId=venue_bank_account_link.venueId,
                bankAccountId=venue_bank_account_link.bankAccountId,
                actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                authorUser=author,
            )
            db.session.add(action_history)
            logger.info(
                "Venue Bank Account Link has been deprecated",
                extra={
                    "venueId": venue_bank_account_link.venueId,
                    "bankAccountId": venue_bank_account_link.bankAccountId,
                },
            )

        if venue_pricing_point_link := venue.current_pricing_point_link:
            venue_pricing_point_link.timespan = db_utils.make_timerange(venue_pricing_point_link.timespan.lower, now)
            logger.info(
                "Venue Pricing Point Link has been deprecated",
                extra={
                    "venueId": venue_pricing_point_link.venueId,
                    "pricingPointId": venue_pricing_point_link.pricingPointId,
                },
            )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--author-id", type=int, help="Author", required=True)
    parser.add_argument("--not-dry", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    author = db.session.query(users_models.User).filter(users_models.User.id == args.author_id).one()

    main(author=author, not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
