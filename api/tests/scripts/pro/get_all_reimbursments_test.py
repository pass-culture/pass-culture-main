import datetime

import pytest

from pcapi.core.finance import factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users.factories import ProFactory
from pcapi.scripts.pro.get_all_reimbursement import _get_all_invoices


@pytest.mark.usefixtures("db_session")
def test_return_all_invoices_linked_to_user():
    user = ProFactory()
    offerer_A = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=offerer_A)
    bank_account_A = finance_factories.BankAccountFactory(offerer=offerer_A)
    venue_A = offerers_factories.VenueFactory(managingOfferer=offerer_A)
    invoice_A1 = finance_factories.InvoiceFactory(bankAccount=bank_account_A, reimbursementPoint=venue_A)
    invoice_A2 = finance_factories.InvoiceFactory(bankAccount=bank_account_A, reimbursementPoint=venue_A)

    other_venue_A = offerers_factories.VenueFactory(managingOfferer=offerer_A)
    invoice_A3 = finance_factories.InvoiceFactory(bankAccount=bank_account_A, reimbursementPoint=other_venue_A)

    offerer_B = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=offerer_B)
    bank_account_B = finance_factories.BankAccountFactory(offerer=offerer_B)
    venue_B = offerers_factories.VenueFactory(managingOfferer=offerer_B)
    invoice_B = finance_factories.InvoiceFactory(bankAccount=bank_account_B, reimbursementPoint=venue_B)

    not_linked_venue = offerers_factories.VenueFactory()
    not_linked_invoice = finance_factories.InvoiceFactory(reimbursementPoint=not_linked_venue)

    invoices = _get_all_invoices(user.id)
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
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    invoice_old = finance_factories.InvoiceFactory(
        bankAccount=bank_account, reimbursementPoint=venue, date=datetime.datetime(2022, 1, 1)
    )
    invoice_new = finance_factories.InvoiceFactory(
        bankAccount=bank_account, reimbursementPoint=venue, date=datetime.datetime.now(datetime.timezone.utc)
    )

    invoices = _get_all_invoices(user.id)
    references = [invoice.reference for invoice in invoices]

    assert len(invoices) == 1
    assert invoice_old.reference not in references
    assert invoice_new.reference in references
