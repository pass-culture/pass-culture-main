import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.users.factories import ProFactory
from pcapi.scripts.pro.upload_reimbursement_csv_to_offerer_drive import _get_all_invoices


@pytest.mark.usefixtures("db_session")
def test_return_all_invoices_linked_to_user():
    user = ProFactory()
    offerer_A = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=offerer_A)
    bank_account_A = finance_factories.BankAccountFactory(offerer=offerer_A)
    batch1 = finance_factories.CashflowBatchFactory(id=1)
    cashflow = finance_factories.CashflowFactory(batch=batch1, bankAccount=bank_account_A, amount=1)
    invoice_A1 = finance_factories.InvoiceFactory(bankAccount=bank_account_A, cashflows=[cashflow])
    invoice_A2 = finance_factories.InvoiceFactory(bankAccount=bank_account_A, cashflows=[cashflow])

    invoice_A3 = finance_factories.InvoiceFactory(bankAccount=bank_account_A, cashflows=[cashflow])

    offerer_B = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=offerer_B)
    bank_account_B = finance_factories.BankAccountFactory(offerer=offerer_B)
    invoice_B = finance_factories.InvoiceFactory(bankAccount=bank_account_B, cashflows=[cashflow])

    not_linked_invoice = finance_factories.InvoiceFactory()

    invoices = _get_all_invoices(user.id, 1)
    references = [invoice.reference for invoice in invoices]

    assert len(invoices) == 4
    assert invoice_A1.reference in references
    assert invoice_A2.reference in references
    assert invoice_A3.reference in references
    assert invoice_B.reference in references
    assert not_linked_invoice.reference not in references


@pytest.mark.usefixtures("db_session")
def test_return_recent_invoices():
    user = ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=offerer)
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    batch1 = finance_factories.CashflowBatchFactory(id=1)
    cashflow = finance_factories.CashflowFactory(batch=batch1, bankAccount=bank_account, amount=1)
    invoice_old = finance_factories.InvoiceFactory(bankAccount=bank_account)
    invoice_new = finance_factories.InvoiceFactory(bankAccount=bank_account, cashflows=[cashflow])

    invoices = _get_all_invoices(user.id, 1)
    references = [invoice.reference for invoice in invoices]

    assert len(invoices) == 1
    assert invoice_old.reference not in references
    assert invoice_new.reference in references
