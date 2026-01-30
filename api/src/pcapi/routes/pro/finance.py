import datetime
from io import BytesIO

import sqlalchemy.orm as sa_orm
from flask_login import current_user
from flask_login import login_required
from pypdf import PdfReader
from pypdf import PdfWriter

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.finance.utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import finance_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import requests
from pcapi.utils import rest
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@private_api.route("/v2/finance/invoices", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=finance_serialize.InvoiceListV2ResponseModel, api=blueprint.pro_private_schema)
def get_invoices_v2(query: finance_serialize.InvoiceListV2QueryModel) -> finance_serialize.InvoiceListV2ResponseModel:
    # Frontend sends a period with *inclusive* bounds, but
    # `get_paid_invoices_query` expects the upper bound to be *exclusive*.
    if query.period_ending_date:
        query.period_ending_date += datetime.timedelta(days=1)
    invoices = finance_repository.get_paid_invoices_query(
        current_user,
        bank_account_id=query.bank_account_id,
        date_from=query.period_beginning_date,
        date_until=query.period_ending_date,
        offerer_id=query.offerer_id,
    )
    invoices = invoices.options(
        sa_orm.joinedload(finance_models.Invoice.cashflows).joinedload(finance_models.Cashflow.batch)
    )
    invoices = invoices.order_by(finance_models.Invoice.date.desc())

    return finance_serialize.InvoiceListV2ResponseModel(
        [
            finance_serialize.InvoiceResponseV2Model(
                reference=invoice.reference,
                date=invoice.date.date(),
                amount=float(-finance_utils.cents_to_full_unit(invoice.amount)),
                url=invoice.url,
                cashflow_labels=[cashflow.batch.label for cashflow in invoice.cashflows],
                bank_account_label=invoice.bankAccount.label,
            )
            for invoice in invoices
        ]
    )


@private_api.route("/v2/finance/has-invoice", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=finance_serialize.HasInvoiceResponseModel, api=blueprint.pro_private_schema)
def has_invoice(query: finance_serialize.HasInvoiceQueryModel) -> finance_serialize.HasInvoiceResponseModel:
    rest.check_user_has_access_to_offerer(current_user, offerer_id=query.offerer_id)
    offerer_has_invoice = finance_repository.has_invoice(query.offerer_id)

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
    invoices = finance_repository.get_invoices_by_references(query.invoice_references)
    if not invoices:
        raise ApiErrors({"invoice": "Invoice not found"}, status_code=404)
    bank_accounts = (
        db.session.query(finance_models.Invoice)
        .join(finance_models.Invoice.bankAccount)
        .filter(finance_models.Invoice.reference.in_(query.invoice_references))
        .with_entities(finance_models.BankAccount.offererId)
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
    merger = PdfWriter()
    tmp = BytesIO()

    for invoice_pdf_url in invoice_pdf_urls:
        try:
            invoice_pdf = PdfReader(BytesIO(requests.get(invoice_pdf_url).content))
        except Exception:
            merger.close()
            raise ApiErrors({"invoice": f"Failed to fetch invoice PDF from url: {invoice_pdf_url}"}, status_code=424)
        merger.append(invoice_pdf)

    merger.write(tmp)
    merger.close()
    return tmp.getvalue()


@private_api.route("/finance/bank-accounts", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=finance_serialize.FinanceBankAccountListResponseModel, api=blueprint.pro_private_schema
)
def get_bank_accounts() -> finance_serialize.FinanceBankAccountListResponseModel:
    bank_accounts = finance_repository.get_bank_accounts_query(user=current_user)
    bank_accounts = bank_accounts.order_by(finance_models.BankAccount.label)
    return finance_serialize.FinanceBankAccountListResponseModel(
        [
            finance_serialize.FinanceBankAccountResponseModel.model_validate(bank_account)
            for bank_account in bank_accounts
        ]
    )
