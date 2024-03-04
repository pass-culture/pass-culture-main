import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class GetInvoicesTest:
    def test_get_invoices(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        dt1 = datetime.datetime(2021, 1, 1)
        invoice1 = finance_factories.InvoiceFactory(bankAccount=bank_account, date=dt1, amount=-1000)
        dt2 = dt1 + datetime.timedelta(days=15)
        invoice2 = finance_factories.InvoiceFactory(bankAccount=bank_account, date=dt2, amount=-1500)
        finance_factories.CashflowFactory(
            invoices=[invoice1, invoice2],
            bankAccount=bank_account,
            amount=-2500,
            batch=finance_factories.CashflowBatchFactory(label="VIR1"),
        )
        _other_bank_account = finance_factories.BankAccountFactory()
        _other_invoice = finance_factories.InvoiceFactory(bankAccount=_other_bank_account)

        client = client.with_session_auth(pro.email)
        response = client.get("/v2/finance/invoices")

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 2
        assert invoices[0] == {
            "reference": invoice2.reference,
            "date": invoice2.date.date().isoformat(),
            "cashflowLabels": ["VIR1"],
            "amount": 15.00,
            "url": invoice2.url,
            "bankAccountLabel": bank_account.label,
        }
        assert invoices[1]["reference"] == invoice1.reference

    def test_get_invoices_only_return_visible_invoices(self, client):
        offerer1 = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        bank_account1 = finance_factories.BankAccountFactory(offerer=offerer1)
        dt1 = datetime.datetime(2021, 1, 1)
        invoice1 = finance_factories.InvoiceFactory(bankAccount=bank_account1, date=dt1, amount=-1000)
        dt2 = dt1 + datetime.timedelta(days=15)
        invoice2 = finance_factories.InvoiceFactory(bankAccount=bank_account1, date=dt2, amount=-1500)
        finance_factories.CashflowFactory(
            invoices=[invoice1, invoice2],
            bankAccount=bank_account1,
            amount=-2500,
            batch=finance_factories.CashflowBatchFactory(label="VIR1"),
        )
        offerer2 = offerers_factories.OffererFactory()
        bank_account2 = finance_factories.BankAccountFactory(offerer=offerer2)
        _other_invoice = finance_factories.InvoiceFactory(bankAccount=bank_account2, amount=-15000000)
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)
        offerers_factories.NotValidatedUserOffererFactory(user=pro, offerer=offerer2)

        client = client.with_session_auth(pro.email)
        response = client.get("/v2/finance/invoices")

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 2
        assert invoices[0] == {
            "reference": invoice2.reference,
            "date": invoice2.date.date().isoformat(),
            "amount": 15.0,
            "cashflowLabels": ["VIR1"],
            "url": invoice2.url,
            "bankAccountLabel": bank_account1.label,
        }
        assert invoices[1] == {
            "reference": invoice1.reference,
            "date": invoice1.date.date().isoformat(),
            "amount": 10.0,
            "cashflowLabels": ["VIR1"],
            "url": invoice1.url,
            "bankAccountLabel": bank_account1.label,
        }

    def test_get_invoices_specify_bank_account(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()

        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account1 = finance_factories.BankAccountFactory(offerer=offerer)
        invoice1 = finance_factories.InvoiceFactory(bankAccount=bank_account1, amount=-1000)
        bank_account2 = finance_factories.BankAccountFactory(offerer=offerer)
        _invoice2 = finance_factories.InvoiceFactory(bankAccount=bank_account2, amount=-1500)

        client = client.with_session_auth(pro.email)
        params = {"bankAccountId": bank_account1.id}
        response = client.get("/v2/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice1.reference

    def test_get_invoices_specify_dates(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        _invoice_before = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 6, 1),
        )
        invoice_within = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 7, 1),
        )
        _invoice_after = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 8, 1),
        )

        client = client.with_session_auth(pro.email)
        params = {"periodBeginningDate": "2021-07-01", "periodEndingDate": "2021-07-31"}
        response = client.get("/v2/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice_within.reference

    def test_get_invoices_unauthorized_bank_account(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        other_bank_account = finance_factories.BankAccountFactory()
        _other_reimbursement_point_invoice = finance_factories.InvoiceFactory(
            bankAccount=other_bank_account, amount=-1000
        )

        client = client.with_session_auth(pro.email)
        params = {"bankAccountId": other_bank_account.id}
        response = client.get("/v2/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert invoices == []

    def test_admin_user_should_access_invoices_if_offerer_id_given(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.AdminFactory()

        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account1 = finance_factories.BankAccountFactory(offerer=offerer)
        finance_factories.InvoiceFactory(bankAccount=bank_account1, amount=-1000)
        bank_account2 = finance_factories.BankAccountFactory(offerer=offerer)
        finance_factories.InvoiceFactory(bankAccount=bank_account2, amount=-1500)

        client = client.with_session_auth(pro.email)
        params = {"offererId": offerer.id}
        response = client.get("/v2/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 2

    def test_filter_both_on_bank_account_and_offerer_should_consider_bank_account(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()

        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account1 = finance_factories.BankAccountFactory(offerer=offerer)
        invoice1 = finance_factories.InvoiceFactory(bankAccount=bank_account1, amount=-1000)
        bank_account2 = finance_factories.BankAccountFactory(offerer=offerer)
        finance_factories.InvoiceFactory(bankAccount=bank_account2, amount=-1500)

        client = client.with_session_auth(pro.email)
        params = {"offererId": offerer.id, "bankAccountId": bank_account1.id}
        response = client.get("/v2/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice1.reference

    def test_do_not_return_invoices_for_admin_user_if_no_filter_on_offerer_or_bank_account(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.AdminFactory()

        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account1 = finance_factories.BankAccountFactory(offerer=offerer)
        finance_factories.InvoiceFactory(bankAccount=bank_account1, amount=-1000)
        bank_account2 = finance_factories.BankAccountFactory(offerer=offerer)
        finance_factories.InvoiceFactory(bankAccount=bank_account2, amount=-1500)

        client = client.with_session_auth(pro.email)
        response = client.get("/v2/finance/invoices")

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 0
