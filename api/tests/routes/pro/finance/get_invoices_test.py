import datetime

import pytest

from pcapi.core import testing
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance.models import InvoiceStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")

URL = "/finance/invoices"


class GetInvoicesTest:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check if user_offerer exists
    num_queries += 1  # check if offerer has invoices
    num_queries += 1  # get invoices

    @pytest.mark.parametrize(
        "offerer_factory", [offerers_factories.OffererFactory, offerers_factories.ClosedOffererFactory]
    )
    def test_get_invoices(self, client: TestClient, offerer_factory):
        offerer = offerer_factory()
        offerer_id = offerer.id
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
        invoice3 = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=dt2 + datetime.timedelta(days=15),
            amount=-2000,
            status=InvoiceStatus.PENDING,
        )
        invoice4 = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=dt2 + datetime.timedelta(days=30),
            amount=-2500,
            status=InvoiceStatus.PENDING_PAYMENT,
        )

        client = client.with_session_auth(pro.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        assert response.json == {
            "hasInvoice": True,
            "invoices": [
                {
                    "reference": invoice4.reference,
                    "date": invoice4.date.date().isoformat(),
                    "amount": 25.0,
                    "url": invoice4.url,
                    "status": "pending_payment",
                },
                {
                    "reference": invoice3.reference,
                    "date": invoice3.date.date().isoformat(),
                    "amount": 20.0,
                    "url": invoice3.url,
                    "status": "pending",
                },
                {
                    "reference": invoice2.reference,
                    "date": invoice2.date.date().isoformat(),
                    "amount": 15.0,
                    "url": invoice2.url,
                    "status": "paid",
                },
                {
                    "reference": invoice1.reference,
                    "date": invoice1.date.date().isoformat(),
                    "amount": 10.0,
                    "url": invoice1.url,
                    "status": "paid",
                },
            ],
        }

    def test_get_invoices_only_return_visible_invoices(self, client: TestClient):
        offerer1 = offerers_factories.OffererFactory()
        offerer_id = offerer1.id
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
        offerers_factories.NewUserOffererFactory(user=pro, offerer=offerer2)

        client = client.with_session_auth(pro.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        assert response.json == {
            "hasInvoice": True,
            "invoices": [
                {
                    "reference": invoice2.reference,
                    "date": invoice2.date.date().isoformat(),
                    "amount": 15.0,
                    "url": invoice2.url,
                    "status": "paid",
                },
                {
                    "reference": invoice1.reference,
                    "date": invoice1.date.date().isoformat(),
                    "amount": 10.0,
                    "url": invoice1.url,
                    "status": "paid",
                },
            ],
        }

    def test_get_invoices_specify_bank_account(self, client: TestClient):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()

        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account1 = finance_factories.BankAccountFactory(offerer=offerer)
        invoice1 = finance_factories.InvoiceFactory(bankAccount=bank_account1, amount=-1000)
        bank_account2 = finance_factories.BankAccountFactory(offerer=offerer)
        _invoice2 = finance_factories.InvoiceFactory(bankAccount=bank_account2, amount=-1500)

        client = client.with_session_auth(pro.email)
        params = {"offererId": offerer.id, "bankAccountId": bank_account1.id}
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 200
        assert response.json["hasInvoice"] is True
        invoices = response.json["invoices"]
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice1.reference

    def test_get_invoices_specify_dates(self, client: TestClient):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        _invoice_before = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 6, 1),
        )
        invoice_lower_bound = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 7, 1),
        )
        invoice_within = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 7, 15),
        )
        invoice_upper_bound = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 7, 31),
        )
        _invoice_after = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.datetime(2021, 8, 1),
        )

        client = client.with_session_auth(pro.email)
        params = {"offererId": offerer.id, "periodBeginningDate": "2021-07-01", "periodEndingDate": "2021-07-31"}
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 200
        assert response.json["hasInvoice"] is True
        invoices = response.json["invoices"]
        assert len(invoices) == 3
        assert {result["reference"] for result in invoices} == {
            invoice_lower_bound.reference,
            invoice_within.reference,
            invoice_upper_bound.reference,
        }

    def test_get_invoices_positive_amount(self, client: TestClient):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        invoice_positive = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            # For the pro user, the amount is the opposite of the db amount
            # See the comment about amounts in src/pcapi/core/finance/models.py:3
            amount=-100,
        )
        _invoice_negative = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            amount=100,
        )

        client = client.with_session_auth(pro.email)
        params = {"offererId": offerer.id, "amountPositiveOnly": True}
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 200
        assert response.json["hasInvoice"] is True
        invoices = response.json["invoices"]
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice_positive.reference

    def test_get_invoices_negative_amount(self, client: TestClient):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        _invoice_positive = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            # For the pro user, the amount is the opposite of the db amount
            # See the comment about amounts in src/pcapi/core/finance/models.py:3
            amount=-100,
        )
        invoice_negative = finance_factories.InvoiceFactory(
            bankAccount=bank_account,
            amount=100,
        )

        client = client.with_session_auth(pro.email)
        params = {"offererId": offerer.id, "amountNegativeOnly": True}
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 200
        assert response.json["hasInvoice"] is True
        invoices = response.json["invoices"]
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice_negative.reference

    def test_get_invoices_unauthorized_bank_account(self, client: TestClient):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        other_bank_account = finance_factories.BankAccountFactory()
        finance_factories.InvoiceFactory(bankAccount=other_bank_account)

        client = client.with_session_auth(pro.email)
        params = {"offererId": offerer.id, "bankAccountId": other_bank_account.id}
        num_queries = self.num_queries - 1  # no query to fetch invoices
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 200
        assert response.json == {"hasInvoice": False, "invoices": []}

    def test_with_no_invoice(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        bank_account = finance_factories.BankAccountFactory()
        finance_factories.InvoiceFactory(bankAccount=bank_account)

        client = client.with_session_auth(user_offerer.user.email)
        params = {"offererId": user_offerer.offerer.id}
        num_queries = self.num_queries - 1  # no query to fetch invoices
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 200
        assert response.json == {"hasInvoice": False, "invoices": []}

    def test_with_invoices_filtered_out(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        bank_account = finance_factories.BankAccountFactory(offerer=user_offerer.offerer)
        other_bank_account = finance_factories.BankAccountFactory(offerer=user_offerer.offerer)
        finance_factories.InvoiceFactory(bankAccount=bank_account)

        client = client.with_session_auth(user_offerer.user.email)
        params = {"offererId": user_offerer.offerer.id, "bankAccountId": other_bank_account.id}
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 200
        assert response.json == {"hasInvoice": True, "invoices": []}

    def test_no_access_to_offerer(self, client: TestClient):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        finance_factories.InvoiceFactory(bankAccount=bank_account)

        client = client.with_session_auth(user.email)
        params = {"offererId": offerer.id}

        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    def test_no_offerer_id(self, client: TestClient):
        user = users_factories.ProFactory()

        client = client.with_session_auth(user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params={})

        assert response.status_code == 400
        assert response.json == {"offererId": ["Ce champ est obligatoire"]}
