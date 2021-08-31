from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.offerers.models import Offerer
from pcapi.flask_app import private_api
from pcapi.models import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerers_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.routes.serialization.reimbursement_csv_serialize import legacy_find_all_offerers_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import validate_reimbursement_period
from pcapi.serialization.utils import dehumanize_id


# @debt api-migration
@private_api.route("/reimbursements/csv", methods=["GET"])
@login_required
def get_reimbursements_csv() -> tuple[bytes, int, dict[str, str]]:
    if FeatureToggle.PRO_REIMBURSEMENTS_FILTERS.is_active():
        reimbursement_details_csv = _get_reimbursements_csv_filter()
    else:
        reimbursement_details_csv = _get_reimbursements_csv_no_filter()

    return (
        reimbursement_details_csv.encode("utf-8-sig"),
        200,
        {
            "Content-type": "text/csv; charset=utf-8;",
            "Content-Disposition": "attachment; filename=remboursements_pass_culture.csv",
        },
    )


def _get_reimbursements_csv_filter() -> str:
    offerers = Offerer.query.with_entities(Offerer.id)
    if not current_user.has_admin_role:
        offerers = filter_query_where_user_is_user_offerer_and_is_validated(offerers, current_user)
    elif not request.args.get("venueId"):
        raise ApiErrors({"venueId": ["Le filtre par lieu est obligatoire pour les administrateurs"]})

    all_offerer_ids = [row[0] for row in offerers.all()]

    reimbursement_period_field_names = ("reimbursementPeriodBeginningDate", "reimbursementPeriodEndingDate")
    reimbursement_period_beginning_date, reimbursement_period_ending_date = validate_reimbursement_period(
        reimbursement_period_field_names, request.args.get
    )
    venue_id = dehumanize_id(request.args.get("venueId"))

    reimbursement_details = find_all_offerers_reimbursement_details(
        all_offerer_ids,
        (reimbursement_period_beginning_date, reimbursement_period_ending_date),
        venue_id,
    )
    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return reimbursement_details_csv


# TODO(AnthonySkorski, 2021-09-15): to be deleted when PRO_REIMBURSEMENTS_FILTERS feature flag is definitely enabled
def _get_reimbursements_csv_no_filter() -> str:
    offerers = Offerer.query.with_entities(Offerer.id)
    offerers = filter_query_where_user_is_user_offerer_and_is_validated(offerers, current_user)
    all_offerer_ids = [row[0] for row in offerers.all()]

    reimbursement_details = legacy_find_all_offerers_reimbursement_details(all_offerer_ids)
    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return reimbursement_details_csv
