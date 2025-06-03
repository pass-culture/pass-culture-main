import datetime

import pytest
import time_machine

from pcapi.core.finance import external
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.dummy import bank_accounts as dummy_bank_accounts
from pcapi.core.finance.backend.dummy import invoices as dummy_invoices
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db


pytestmark = [
    pytest.mark.usefixtures("db_session", "clean_dummy_backend_data"),
    pytest.mark.features(
        WIP_ENABLE_NEW_FINANCE_WORKFLOW=True,
        ENABLE_BANK_ACCOUNT_SYNC=True,
        ENABLE_INVOICE_SYNC=True,
    ),
]


class ExternalFinanceTest:
    def test_push_bank_accounts(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        assert bank_account.lastCegidSyncDate is None

        now = datetime.datetime.utcnow()
        with time_machine.travel(now, tick=False):
            external.push_bank_accounts(10)
        db.session.flush()
        db.session.refresh(bank_account)
        assert bank_account.lastCegidSyncDate == now
        assert len(dummy_bank_accounts) == 1
        assert dummy_bank_accounts[0] == bank_account

    def test_push_invoices(self):
        invoice1 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.PENDING, cashflows=[finance_factories.CashflowFactory()]
        )
        invoice2 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.PAID, cashflows=[finance_factories.CashflowFactory()]
        )
        invoice3 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.PENDING_PAYMENT, cashflows=[finance_factories.CashflowFactory()]
        )
        invoice4 = finance_factories.InvoiceFactory(
            status=finance_models.InvoiceStatus.REJECTED, cashflows=[finance_factories.CashflowFactory()]
        )

        external.push_invoices(10)
        db.session.flush()
        db.session.refresh(invoice1)
        db.session.refresh(invoice2)
        db.session.refresh(invoice3)
        db.session.refresh(invoice4)
        assert invoice1.status == finance_models.InvoiceStatus.PAID
        assert invoice2.status == finance_models.InvoiceStatus.PAID
        assert invoice3.status == finance_models.InvoiceStatus.PENDING_PAYMENT
        assert invoice4.status == finance_models.InvoiceStatus.REJECTED

        assert len(dummy_invoices) == 1
        assert dummy_invoices[0] == invoice1


class ExternalFinanceCommandTest:
    def test_push_bank_accounts_command(self, run_command, mocker):
        push_bank_accounts_mock = mocker.patch("pcapi.core.finance.external.push_bank_accounts")
        run_command("push_bank_accounts", raise_on_error=True)

        assert push_bank_accounts_mock.call_count == 1

    @pytest.mark.features(ENABLE_BANK_ACCOUNT_SYNC=False)
    def test_push_bank_accounts_command_feature_toggle(self, run_command, mocker):
        push_bank_accounts_mock = mocker.patch("pcapi.core.finance.external.push_bank_accounts")
        run_command("push_bank_accounts", raise_on_error=True)

        assert push_bank_accounts_mock.call_count == 0

    @pytest.mark.features(ENABLE_INVOICE_SYNC=False)
    def test_push_invoices_command_feature_toggle(self, run_command, mocker):
        push_invoices_mock = mocker.patch("pcapi.core.finance.external.push_invoices")
        run_command("push_invoices", raise_on_error=True)

        assert push_invoices_mock.call_count == 0

    def test_push_invoices_command(self, run_command, mocker):
        push_invoices_mock = mocker.patch("pcapi.core.finance.external.push_invoices")
        run_command("push_invoices", raise_on_error=True)

        assert push_invoices_mock.call_count == 1
