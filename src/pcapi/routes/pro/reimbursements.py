from datetime import date
from itertools import chain

from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.offerers.models import Offerer
from pcapi.flask_app import private_api
from pcapi.models.feature import FeatureToggle
from pcapi.repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.routes.serialization.reimbursement_csv_serialize import legacy_find_all_offerer_reimbursement_details
from pcapi.utils.human_ids import dehumanize


# @debt api-migration
@private_api.route("/reimbursements/csv", methods=["GET"])
@login_required
def get_reimbursements_csv():
    query = filter_query_where_user_is_user_offerer_and_is_validated(Offerer.query, current_user)

    all_validated_offerers_for_the_current_user = query.all()

    # FIXME: due to generalisation, the performance issue has led to DDOS many
    # users checking the many bookings of these offerers
    temporarily_banned_sirens = ["334473352", "434001954", "343282380"]
    if FeatureToggle.DISABLE_BOOKINGS_RECAP_FOR_SOME_PROS.is_active():
        if any(offerer.siren in temporarily_banned_sirens for offerer in all_validated_offerers_for_the_current_user):
            # Here we use the same process as for admins
            all_validated_offerers_for_the_current_user = []

    if FeatureToggle.PRO_REIMBURSEMENTS_FILTERS.is_active():
        reimbursement_period_beginning_date = date.fromisoformat(request.args.get("reimbursementPeriodBeginningDate"))
        reimbursement_period_ending_date = date.fromisoformat(request.args.get("reimbursementPeriodEndingDate"))
        venue_id = dehumanize(request.args.get("venueId"))

        reimbursement_details = chain(
            *[
                find_all_offerer_reimbursement_details(
                    offerer.id, (reimbursement_period_beginning_date, reimbursement_period_ending_date), venue_id
                )
                for offerer in all_validated_offerers_for_the_current_user
            ]
        )
    else:
        reimbursement_details = chain(
            *[
                legacy_find_all_offerer_reimbursement_details(offerer.id)
                for offerer in all_validated_offerers_for_the_current_user
            ]
        )

    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return (
        reimbursement_details_csv.encode("utf-8-sig"),
        200,
        {
            "Content-type": "text/csv; charset=utf-8;",
            "Content-Disposition": "attachment; filename=remboursements_pass_culture.csv",
        },
    )
