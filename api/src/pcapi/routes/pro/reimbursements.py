from flask_login import current_user
from flask_login import login_required

from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerer_models
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementCsvByInvoicesModel
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementCsvQueryModel
from pcapi.routes.serialization.reimbursement_csv_serialize import find_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import find_reimbursement_details_by_invoices
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.routes.serialization.reimbursement_csv_serialize import validate_reimbursement_period
from pcapi.serialization.decorator import spectree_serialize

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
    if not user.has_admin_role:
        if not user.has_access(query.offererId):
            raise ApiErrors({"offererId": ["Cet utilisateur ne peut pas accèder à cette structure"]})
    elif not query.bankAccountId:
        raise ApiErrors({"bankAccountId": ["Le filtre par compte bancaire est obligatoire pour les administrateurs"]})

    reimbursement_period_field_names = ("reimbursementPeriodBeginningDate", "reimbursementPeriodEndingDate")
    reimbursement_period_beginning_date, reimbursement_period_ending_date = validate_reimbursement_period(
        reimbursement_period_field_names, query.dict().get
    )
    bank_account_id = query.bankAccountId

    reimbursement_details = find_offerer_reimbursement_details(
        query.offererId,
        (reimbursement_period_beginning_date, reimbursement_period_ending_date),
        bank_account_id,
    )
    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return reimbursement_details_csv


@private_api.route("/v2/reimbursements/csv", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8;",
        "Content-Disposition": "attachment; filename=remboursements_pass_culture.csv",
    },
    api=blueprint.pro_private_schema,
    flatten=True,
)
def get_reimbursements_csv_v2(query: ReimbursementCsvByInvoicesModel) -> bytes:
    reimbursement_details_csv = _get_reimbursments_csv_filter_by_invoices(current_user, query)
    return reimbursement_details_csv.encode("utf-8-sig")


def _get_reimbursments_csv_filter_by_invoices(user: User, query: ReimbursementCsvByInvoicesModel) -> str:
    offerers = (
        finance_models.Invoice.query.join(finance_models.Invoice.bankAccount)
        .join(finance_models.BankAccount.offerer)
        .filter(finance_models.Invoice.reference.in_(query.invoicesReferences))
        .with_entities(offerer_models.Offerer.id)
        .all()
    )
    offerer_ids = {offerer.id for offerer in offerers}
    if not offerer_ids:
        raise ApiErrors({"invoicesReferences": ["Aucune structure trouvée pour les factures fournies"]})
    if not user.has_admin_role:
        for offerer_id in offerer_ids:
            if not user.has_access(offerer_id):
                raise ApiErrors({"offererId": ["Cet utilisateur ne peut pas accèder à cette structure"]})

    reimbursement_details = find_reimbursement_details_by_invoices(query.invoicesReferences)
    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return reimbursement_details_csv
