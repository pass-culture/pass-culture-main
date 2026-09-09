from flask_login import current_user
from flask_login import login_required

from pcapi.core.finance import models
from pcapi.core.finance import repository
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import finance_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import pdf
from pcapi.utils import rest
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@private_api.route("/finance/settlements", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=finance_serialize.SettlementListResponseModel, api=blueprint.pro_private_schema)
def get_settlements(query: finance_serialize.SettlementListQueryModel) -> finance_serialize.SettlementListResponseModel:
    rest.check_user_has_access_to_offerer(current_user, offerer_id=query.offerer_id)

    settlements_query = repository.get_settlements_query(
        offerer_id=query.offerer_id,
        bank_account_id=query.bank_account_id,
        date_from=query.period_beginning_date,
        date_until=query.period_ending_date,
        name_search=query.name_search,
    )

    return finance_serialize.SettlementListResponseModel(
        [finance_serialize.SettlementResponseModel.build(settlement) for settlement in settlements_query]
    )


@private_api.route("/finance/has-settlement", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=finance_serialize.HasSettlementResponseModel, api=blueprint.pro_private_schema)
def has_settlement(query: finance_serialize.HasSettlementQueryModel) -> finance_serialize.HasSettlementResponseModel:
    rest.check_user_has_access_to_offerer(current_user, offerer_id=query.offerer_id)

    offerer_has_settlement = repository.has_settlement(offerer_id=query.offerer_id)

    return finance_serialize.HasSettlementResponseModel(has_settlement=offerer_has_settlement)


@private_api.route("/v2/finance/invoices", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=finance_serialize.InvoiceListV2ResponseModel, api=blueprint.pro_private_schema)
def get_invoices_v2(query: finance_serialize.InvoiceListV2QueryModel) -> finance_serialize.InvoiceListV2ResponseModel:
    invoices = repository.get_paid_invoices_query(
        current_user,
        bank_account_id=query.bank_account_id,
        date_from=query.period_beginning_date,
        date_until=query.period_ending_date,
        offerer_id=query.offerer_id,
        # see the comment about amounts in src/pcapi/core/finance/models.py docstring
        amount_lower_than=0 if query.amount_positive_only else None,
        amount_greater_than_equal=0 if query.amount_negative_only else None,
    )

    return finance_serialize.InvoiceListV2ResponseModel(
        [finance_serialize.InvoiceResponseV2Model.build(invoice) for invoice in invoices]
    )


@private_api.route("/v2/finance/has-invoice", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=finance_serialize.HasInvoiceResponseModel, api=blueprint.pro_private_schema)
def has_invoice(query: finance_serialize.HasInvoiceQueryModel) -> finance_serialize.HasInvoiceResponseModel:
    rest.check_user_has_access_to_offerer(current_user, offerer_id=query.offerer_id)

    offerer_has_invoice = repository.has_invoice(query.offerer_id)

    return finance_serialize.HasInvoiceResponseModel(has_invoice=offerer_has_invoice)


@private_api.route("/finance/combined-invoices", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    api=blueprint.pro_private_schema,
    json_format=False,
    response_headers={
        "Content-Type": "application/pdf; charset=utf-8;",
        "Content-Disposition": "attachment; filename=justificatifs_de_remboursement.pdf",
    },
    query_params_as_list=["invoiceReferences"],
)
def get_combined_invoices(query: finance_serialize.GetCombinedInvoicesQueryModel) -> bytes:
    invoices = (
        db.session.query(models.Invoice)
        .filter(models.Invoice.reference.in_(query.invoice_references))
        .order_by(models.Invoice.date)
        .all()
    )
    if not invoices:
        raise ApiErrors({"invoice": "Invoice not found"}, status_code=404)

    bank_accounts = (
        db.session.query(models.Invoice)
        .join(models.Invoice.bankAccount)
        .filter(models.Invoice.reference.in_(query.invoice_references))
        .with_entities(models.BankAccount.offererId)
        .all()
    )
    offerer_ids = {bank_account.offererId for bank_account in bank_accounts}
    if not offerer_ids:
        raise ApiErrors({"invoiceReferences": ["Aucune structure trouvée pour les factures fournies"]})
    if not current_user.has_admin_role:
        user_offerers_count = (
            db.session.query(offerers_models.UserOfferer)
            .filter(
                offerers_models.UserOfferer.userId == current_user.id,
                offerers_models.UserOfferer.offererId.in_(offerer_ids),
                offerers_models.UserOfferer.isValidated,
            )
            .count()
        )
        if user_offerers_count != len(offerer_ids):
            raise ApiErrors({"offererId": ["Cet utilisateur ne peut pas accéder à cette structure"]})

    invoice_pdf_urls = [invoice.url for invoice in invoices]
    try:
        return pdf.merge_pdf_files(invoice_pdf_urls)
    except FileNotFoundError as exc:
        raise ApiErrors({"invoice": f"Failed to fetch invoice PDF from url: {exc}"}, status_code=424)
