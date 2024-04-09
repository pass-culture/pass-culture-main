import datetime

from flask_login import current_user
from flask_login import login_required
import sqlalchemy.orm as sqla_orm

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import finance_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import rest

from . import blueprint


@private_api.route("/v2/finance/invoices", methods=["GET"])
@login_required
@spectree_serialize(response_model=finance_serialize.InvoiceListV2ResponseModel, api=blueprint.pro_private_schema)
def get_invoices_v2(query: finance_serialize.InvoiceListV2QueryModel) -> finance_serialize.InvoiceListV2ResponseModel:
    # Frontend sends a period with *inclusive* bounds, but
    # `get_invoices_query` expects the upper bound to be *exclusive*.
    if query.periodEndingDate:
        query.periodEndingDate += datetime.timedelta(days=1)
    invoices = finance_repository.get_invoices_query(
        current_user,
        bank_account_id=query.bankAccountId,
        date_from=query.periodBeginningDate,
        date_until=query.periodEndingDate,
        offerer_id=query.offererId,
    )
    invoices = invoices.options(
        sqla_orm.joinedload(finance_models.Invoice.cashflows).joinedload(finance_models.Cashflow.batch)
    )
    invoices = invoices.order_by(finance_models.Invoice.date.desc())

    return finance_serialize.InvoiceListV2ResponseModel(
        __root__=[finance_serialize.InvoiceResponseV2Model.from_orm(invoice) for invoice in invoices]
    )


@private_api.route("/v2/finance/has-invoice", methods=["GET"])
@login_required
@spectree_serialize(response_model=finance_serialize.HasInvoiceResponseModel, api=blueprint.pro_private_schema)
def has_invoice(query: finance_serialize.HasInvoiceQueryModel) -> finance_serialize.HasInvoiceResponseModel:
    rest.check_user_has_access_to_offerer(current_user, offerer_id=query.offererId)
    offerer_has_invoice = finance_repository.has_invoice(query.offererId)

    return finance_serialize.HasInvoiceResponseModel(hasInvoice=offerer_has_invoice)


@private_api.route("/finance/bank-accounts", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=finance_serialize.FinanceBankAccountListResponseModel, api=blueprint.pro_private_schema
)
def get_bank_accounts() -> finance_serialize.FinanceBankAccountListResponseModel:
    bank_accounts = finance_repository.get_bank_accounts_query(user=current_user)
    bank_accounts = bank_accounts.order_by(finance_models.BankAccount.label)
    return finance_serialize.FinanceBankAccountListResponseModel(
        __root__=[
            finance_serialize.FinanceBankAccountResponseModel.from_orm(bank_account) for bank_account in bank_accounts
        ],
    )
