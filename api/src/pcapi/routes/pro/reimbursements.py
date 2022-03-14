from flask_login import current_user
from flask_login import login_required

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementCsvQueryModel
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerers_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.routes.serialization.reimbursement_csv_serialize import validate_reimbursement_period
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.utils import dehumanize_id

from . import blueprint


@private_api.route("/reimbursements/csv", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8;",
        "Content-Disposition": "attachment; filename=remboursements_pass_culture.csv",
    },
    api=blueprint.pro_private_schema,
)
def get_reimbursements_csv(query: ReimbursementCsvQueryModel) -> bytes:
    reimbursement_details_csv = _get_reimbursements_csv_filter(current_user, query)
    return reimbursement_details_csv.encode("utf-8-sig")


def _get_reimbursements_csv_filter(user: User, query: ReimbursementCsvQueryModel) -> str:
    offerers = Offerer.query.with_entities(Offerer.id)
    if not user.has_admin_role:
        offerers = filter_query_where_user_is_user_offerer_and_is_validated(offerers, user)
    elif not query.venueId:
        raise ApiErrors({"venueId": ["Le filtre par lieu est obligatoire pour les administrateurs"]})

    all_offerer_ids = [row[0] for row in offerers.all()]

    reimbursement_period_field_names = ("reimbursementPeriodBeginningDate", "reimbursementPeriodEndingDate")
    reimbursement_period_beginning_date, reimbursement_period_ending_date = validate_reimbursement_period(
        reimbursement_period_field_names, query.dict().get
    )
    venue_id = dehumanize_id(query.venueId)

    reimbursement_details = find_all_offerers_reimbursement_details(
        all_offerer_ids,
        (reimbursement_period_beginning_date, reimbursement_period_ending_date),
        venue_id,
    )
    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return reimbursement_details_csv
