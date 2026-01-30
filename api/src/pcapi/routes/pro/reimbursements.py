from flask_login import current_user
from flask_login import login_required

from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerer_models
from pcapi.core.users import repository as users_repository
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementCsvByInvoicesModel
from pcapi.routes.serialization.reimbursement_csv_serialize import find_reimbursement_details_by_invoices
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@private_api.route("/v2/reimbursements/csv", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8;",
        "Content-Disposition": "attachment; filename=remboursements_pass_culture.csv",
    },
    api=blueprint.pro_private_schema,
    query_params_as_list=["invoicesReferences"],
)
def get_reimbursements_csv_v2(query: ReimbursementCsvByInvoicesModel) -> bytes:
    offerers_ids = _get_invoices_offerers(query)
    if not offerers_ids:
        raise ApiErrors({"invoicesReferences": ["Aucune structure trouvée pour les factures fournies"]})

    for offerer_id in offerers_ids:
        if not users_repository.has_access(current_user, offerer_id):
            raise ApiErrors({"offererId": ["Cet utilisateur ne peut pas accèder à cette structure"]})

    reimbursement_details = find_reimbursement_details_by_invoices(query.invoicesReferences)
    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return reimbursement_details_csv.encode("utf-8-sig")


def _get_invoices_offerers(query: ReimbursementCsvByInvoicesModel) -> set[int]:
    offerers = (
        db.session.query(finance_models.Invoice)
        .join(finance_models.Invoice.bankAccount)
        .join(finance_models.BankAccount.offerer)
        .filter(finance_models.Invoice.reference.in_(query.invoicesReferences))
        .with_entities(offerer_models.Offerer.id)
        .all()
    )
    return {offerer.id for offerer in offerers}
