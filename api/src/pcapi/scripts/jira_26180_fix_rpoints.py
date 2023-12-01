# fmt: off
from pcapi.utils import sentry


sentry.init_sentry_sdk = lambda: None
from pcapi.flask_app import app;app.app_context().push()
# fmt: on

import datetime
import sys
import time

import sqlalchemy as sqla

from pcapi import settings
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.models as users_models
from pcapi.models import db
import pcapi.utils.db as db_utils


NOW = datetime.datetime.utcnow()

COMMENT_WITH_BANK_INFO = """Le lieu {venue_id} avait le lieu {reimbursement_point_id} comme point de remboursement. Or le dossier de coordonnées bancaires ({bank_info_id} en interne, {dms_id} côté Démarches Simplifiées) de ce point de remboursement n'était pas accepté. Ce point de remboursement n'avait aucun flux monétaire associé. Une correction massive de données a été faite pour que le lieu {reimbursement_point_id} ne soit plus un point de remboursement. Le lieu {venue_id} n'a donc plus de point de remboursement. Cf. ticket Jira PC-26180 pour plus de détails."""

COMMENT_WITHOUT_BANK_INFO = """Le lieu {venue_id} avait le lieu {reimbursement_point_id} comme point de remboursement. Or ce dernier n'avait aucun dossier de coordonnées bancaires. Il n'avait aucun flux monétaire associé. Une correction massive de données a été faite pour que le lieu {reimbursement_point_id} ne soit plus un point de remboursement. Le lieu {venue_id} n'a donc plus de point de remboursement. Cf. ticket Jira PC-26180 pour plus de détails."""


user_email = sys.argv[1]
USER = users_models.User.query.filter_by(email=user_email).one()


def fix_reimbursement_point(reimbursement_point_id: int) -> None:
    rpoint = offerers_models.Venue.query.options(
        sqla.orm.joinedload(offerers_models.Venue.managingOfferer),
        sqla.orm.joinedload(offerers_models.Venue.bankInformation),
    ).get(reimbursement_point_id)

    bank_info = rpoint.bankInformation
    end_date = bank_info.dateModified if bank_info else NOW

    target_venues = (
        offerers_models.Venue.query.join(offerers_models.Venue.reimbursement_point_links)
        .filter(
            offerers_models.VenueReimbursementPointLink.reimbursementPointId == reimbursement_point_id,
            offerers_models.VenueReimbursementPointLink.timespan.contains(NOW),
        )
        .options(
            sqla.orm.joinedload(offerers_models.Venue.reimbursement_point_links),
        )
    )
    for venue in target_venues:
        if bank_info:
            comment = COMMENT_WITH_BANK_INFO.format(
                venue_id=venue.id,
                reimbursement_point_id=reimbursement_point_id,
                bank_info_id=bank_info.id,
                dms_id=bank_info.applicationId,
                end_date=end_date,
            )
        else:
            comment = COMMENT_WITHOUT_BANK_INFO.format(
                venue_id=venue.id,
                reimbursement_point_id=reimbursement_point_id,
            )

        rpoint_link = venue.current_reimbursement_point_link
        assert rpoint_link.reimbursementPointId == reimbursement_point_id
        rpoint_link.timespan = db_utils.make_timerange(
            rpoint_link.timespan.lower,
            # In some cases (or maybe all?), the link was created just
            # after the last modification time of the BankInfo. So the
            # lower bound of the timespan is slightly _after_ the
            # modification time. In that cas, we cannot use the
            # modification time as the upper bound (because it must be
            # after the lower bound), so we use the lower bound instead.
            # Also, add 1 second. Otherwise, if the upper bound has the
            # same value as the lower bound, the resulting tsrange object
            # is empty because the lower bound is inclusive but the upper
            # bound is not.
            max(end_date, rpoint_link.timespan.lower) + datetime.timedelta(seconds=1),
        )
        db.session.flush()
        action = history_api.log_action(
            action_type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            author=USER,
            offerer=venue.managingOfferer,
            venue=venue,
            comment=comment,
            save=False,
        )
        db.session.add(action)
        db.session.flush()
        print(f"Reimbursement point {reimbursement_point_id}: ended rpoint link {rpoint_link.id} as of {end_date}")


def get_reimbursement_points_to_fix() -> list[int]:
    """Return ids of reimbursement points that have a non-accepted
    BankInformation (or no BankInformation)
    """
    query = """
      with rpoint as (
        select distinct("reimbursementPointId") as id from venue_reimbursement_point_link
        where upper(timespan) is null
      )
      select distinct(rpoint.id) from rpoint
      left outer join bank_information on bank_information."venueId" = rpoint.id
      left outer join cashflow ON cashflow."reimbursementPointId" = rpoint.id
      where
        (
          bank_information.status is null
          or bank_information.status != 'ACCEPTED'
        )
        and cashflow.id is null
        order by 1
    """
    result = db.session.execute(query)
    rows = result.fetchall()
    return sorted(row[0] for row in rows)


def fix_all(save: bool) -> None:
    if save:
        print(f"THIS IS REAL, on {settings.ENV.upper()} you have 5 seconds to interrupt.")
        time.sleep(5)

    rpoints_to_fix = get_reimbursement_points_to_fix()
    print(f"Found {len(rpoints_to_fix)} reimbursements to fix")
    for rpoint_id in rpoints_to_fix:
        fix_reimbursement_point(rpoint_id)

    if save:
        db.session.commit()
        print("That was REAL. Changes have been applied")
    else:
        rpoints_to_fix = get_reimbursement_points_to_fix()
        if rpoints_to_fix:
            print(f"Left: {len(rpoints_to_fix)}. First 10: {rpoints_to_fix[:10]}")

        db.session.rollback()
        print("DRY RUN -- changes have been rolled back")


fix_all(save="--save" in sys.argv[1:])
