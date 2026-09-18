import datetime

import pytest

from pcapi.core import testing
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE
from pcapi.utils.date import get_naive_utc_now

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")

URL = "/finance/settlements"


class GetSettlementsTest:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check if user_offerer exists
    num_queries += 1  # get settlements

    def test_get_settlements(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        bank_account_1 = factories.BankAccountFactory(label="account 1", offerer=user_offerer.offerer)
        bank_account_2 = factories.BankAccountFactory(label="account 2", offerer=user_offerer.offerer)

        batch_1 = factories.SettlementBatchFactory(
            name="VIR1", dateValidated=get_naive_utc_now() - datetime.timedelta(days=1)
        )
        batch_2 = factories.SettlementBatchFactory(
            name="VIR2", dateValidated=get_naive_utc_now() - datetime.timedelta(days=2)
        )
        # this batch name will be displayed as VIR3
        batch_3 = factories.SettlementBatchFactory(
            name="VIR3-1", dateValidated=get_naive_utc_now() - datetime.timedelta(days=3)
        )

        executed_settlement_1 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            amount=10000,
            bankAccount=bank_account_1,
            batch=batch_2,
        )
        executed_settlement_2 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            amount=20000,
            bankAccount=bank_account_2,
            batch=batch_1,
        )
        # add invoices to the settlement
        paid_invoice_1 = factories.InvoiceFactory(
            status=models.InvoiceStatus.PAID,
            reference="F301234567",
            amount=-10000,
            date=get_naive_utc_now() - datetime.timedelta(days=2),
            bankAccount=bank_account_2,
            settlements=[executed_settlement_2],
        )
        paid_invoice_2 = factories.InvoiceFactory(
            status=models.InvoiceStatus.PAID,
            reference="F301234568",
            amount=-10000,
            date=get_naive_utc_now() - datetime.timedelta(days=1),
            bankAccount=bank_account_2,
            settlements=[executed_settlement_2],
        )
        # these two non-paid invoices will no appear in the result
        factories.InvoiceFactory(
            status=models.InvoiceStatus.PENDING, bankAccount=bank_account_2, settlements=[executed_settlement_2]
        )
        factories.InvoiceFactory(
            status=models.InvoiceStatus.PENDING_PAYMENT, bankAccount=bank_account_2, settlements=[executed_settlement_2]
        )
        rejected_settlement = factories.SettlementFactory(
            status=models.SettlementStatus.REJECTED,
            amount=30000,
            bankAccount=bank_account_1,
            batch=batch_3,
        )

        # an issued settlement should not appear in the result
        factories.SettlementFactory(status=models.SettlementStatus.ISSUED, bankAccount=bank_account_1)
        # a settlement linked to another offerer should not appear in the result
        factories.SettlementFactory(status=models.SettlementStatus.EXECUTED)

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id

        num_queries = self.num_queries
        num_queries += 1  # selectinload invoices
        num_queries += 1  # selectinload invoices -> settlements
        num_queries += 1  # selectinload venue bank account links
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        # settlements and invoices are sorted by descending date
        assert response.json == [
            {
                "id": executed_settlement_2.id,
                "label": "VIR1",
                "date": batch_1.dateValidated.date().isoformat(),
                "amount": 200,
                "bankAccount": "account 2",
                "status": "EXECUTED",
                "invoices": [
                    {
                        "reference": "F301234568",
                        "date": paid_invoice_2.date.date().isoformat(),
                        "amount": 100,
                        "url": paid_invoice_2.url,
                        "status": "paid",
                    },
                    {
                        "reference": "F301234567",
                        "date": paid_invoice_1.date.date().isoformat(),
                        "amount": 100,
                        "url": paid_invoice_1.url,
                        "status": "paid",
                    },
                ],
                "resolvedBy": [],
            },
            {
                "id": executed_settlement_1.id,
                "label": "VIR2",
                "date": batch_2.dateValidated.date().isoformat(),
                "amount": 100,
                "bankAccount": "account 1",
                "status": "EXECUTED",
                "invoices": [],
                "resolvedBy": [],
            },
            {
                "id": rejected_settlement.id,
                "label": "VIR3",
                "date": batch_3.dateValidated.date().isoformat(),
                "amount": 300,
                "bankAccount": "account 1",
                "status": "REJECTED_SOLVED",
                "invoices": [],
                "resolvedBy": [],
            },
        ]

    def test_get_settlements_rejected(self, client: TestClient):
        now = get_naive_utc_now()

        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, pricing_point="self")

        # bank account is refused, venue was detached 5 days ago
        bank_account = factories.BankAccountFactory(
            offerer=user_offerer.offerer, status=models.BankAccountApplicationStatus.REFUSED
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=bank_account,
            timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
        )

        # the batch occurred 5 days ago and the settlement is rejected, in sync with the bank account status
        batch = factories.SettlementBatchFactory(name="VIR1", dateValidated=now - datetime.timedelta(days=5))
        invoice = factories.InvoiceFactory(amount=-10000, bankAccount=bank_account, date=batch.dateValidated)
        settlement = factories.SettlementFactory(
            status=models.SettlementStatus.REJECTED,
            amount=10000,
            bankAccount=bank_account,
            batch=batch,
            invoices=[invoice],
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id

        num_queries = self.num_queries
        num_queries += 1  # selectinload venue bank account links
        num_queries += 1  # selectinload invoices
        num_queries += 1  # selectinload venue bank account links -> venue -> links
        num_queries += 1  # selectinload invoices -> settlements
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        # the settlement is "rejected" as the venue is not linked to a bank account
        assert response.json == [
            {
                "id": settlement.id,
                "label": "VIR1",
                "date": batch.dateValidated.date().isoformat(),
                "amount": 100,
                "bankAccount": bank_account.label,
                "status": "REJECTED",
                "invoices": [
                    {
                        "reference": invoice.reference,
                        "date": invoice.date.date().isoformat(),
                        "amount": 100,
                        "url": invoice.url,
                        "status": "paid",
                    },
                ],
                "resolvedBy": [],
            },
        ]

    def test_get_settlements_rejected_processed_solved(self, client: TestClient):
        now = get_naive_utc_now()

        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, pricing_point="self")

        # bank account is refused, venue was detached 5 days ago
        bank_account = factories.BankAccountFactory(
            offerer=user_offerer.offerer, status=models.BankAccountApplicationStatus.REFUSED
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=bank_account,
            timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
        )

        # the batch occurred 5 days ago with 2 rejected settlements, in sync with the bank account status
        batch = factories.SettlementBatchFactory(name="VIR1", dateValidated=now - datetime.timedelta(days=5))
        invoice_1 = factories.InvoiceFactory(amount=-5000, bankAccount=bank_account, date=batch.dateValidated)
        invoice_2 = factories.InvoiceFactory(amount=-5000, bankAccount=bank_account, date=batch.dateValidated)
        settlement_1 = factories.SettlementFactory(
            status=models.SettlementStatus.REJECTED,
            amount=10000,
            bankAccount=bank_account,
            batch=batch,
            invoices=[invoice_1, invoice_2],
        )
        invoice_3 = factories.InvoiceFactory(amount=-2000, bankAccount=bank_account, date=batch.dateValidated)
        settlement_2 = factories.SettlementFactory(
            status=models.SettlementStatus.REJECTED,
            amount=2000,
            bankAccount=bank_account,
            batch=batch,
            invoices=[invoice_3],
        )

        # another valid bank account is now linked to the venue
        new_bank_account = factories.BankAccountFactory(offerer=user_offerer.offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue, bankAccount=new_bank_account, timespan=[now - datetime.timedelta(days=4), None]
        )

        # two new settlements are executed on the new bank account, linked to the first rejected settlement invoices
        new_batch_1 = factories.SettlementBatchFactory(name="VIR2", dateValidated=now - datetime.timedelta(days=3))
        new_batch_2 = factories.SettlementBatchFactory(name="VIR3", dateValidated=now - datetime.timedelta(days=3))
        settlement_3 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            amount=5000,
            bankAccount=new_bank_account,
            batch=new_batch_1,
            invoices=[invoice_1],
        )
        settlement_4 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            amount=5000,
            bankAccount=new_bank_account,
            batch=new_batch_2,
            invoices=[invoice_2],
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id

        num_queries = self.num_queries
        num_queries += 1  # selectinload venue bank account links
        num_queries += 1  # selectinload invoices
        num_queries += 1  # selectinload venue bank account links -> venue -> links
        num_queries += 1  # selectinload invoices -> settlements
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        result = sorted(response.json, key=lambda s: s["id"])
        assert result == [
            # the first settlement is "solved" by the two new settlements
            {
                "id": settlement_1.id,
                "label": "VIR1",
                "date": batch.dateValidated.date().isoformat(),
                "amount": 100,
                "bankAccount": bank_account.label,
                "status": "REJECTED_SOLVED",
                "invoices": [
                    {
                        "reference": invoice_1.reference,
                        "date": invoice_1.date.date().isoformat(),
                        "amount": 50,
                        "url": invoice_1.url,
                        "status": "paid",
                    },
                    {
                        "reference": invoice_2.reference,
                        "date": invoice_2.date.date().isoformat(),
                        "amount": 50,
                        "url": invoice_2.url,
                        "status": "paid",
                    },
                ],
                "resolvedBy": ["VIR2", "VIR3"],
            },
            # the second settlement is "processed" as the venue is linked to a new bank account
            {
                "id": settlement_2.id,
                "label": "VIR1",
                "date": batch.dateValidated.date().isoformat(),
                "amount": 20,
                "bankAccount": bank_account.label,
                "status": "REJECTED_PROCESSED",
                "invoices": [
                    {
                        "reference": invoice_3.reference,
                        "date": invoice_3.date.date().isoformat(),
                        "amount": 20,
                        "url": invoice_3.url,
                        "status": "paid",
                    },
                ],
                "resolvedBy": [],
            },
            {
                "id": settlement_3.id,
                "label": "VIR2",
                "date": new_batch_1.dateValidated.date().isoformat(),
                "amount": 50,
                "bankAccount": new_bank_account.label,
                "status": "EXECUTED",
                "invoices": [
                    {
                        "reference": invoice_1.reference,
                        "date": invoice_1.date.date().isoformat(),
                        "amount": 50,
                        "url": invoice_1.url,
                        "status": "paid",
                    },
                ],
                "resolvedBy": [],
            },
            {
                "id": settlement_4.id,
                "label": "VIR3",
                "date": new_batch_2.dateValidated.date().isoformat(),
                "amount": 50,
                "bankAccount": new_bank_account.label,
                "status": "EXECUTED",
                "invoices": [
                    {
                        "reference": invoice_2.reference,
                        "date": invoice_2.date.date().isoformat(),
                        "amount": 50,
                        "url": invoice_2.url,
                        "status": "paid",
                    },
                ],
                "resolvedBy": [],
            },
        ]

    def test_get_settlements_bank_account_filter(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        bank_account_1 = factories.BankAccountFactory(offerer=user_offerer.offerer)
        bank_account_2 = factories.BankAccountFactory(offerer=user_offerer.offerer)
        settlement_1 = factories.SettlementFactory(status=models.SettlementStatus.EXECUTED, bankAccount=bank_account_1)
        # linked to other bank account, should not appear in the result
        factories.SettlementFactory(status=models.SettlementStatus.EXECUTED, bankAccount=bank_account_2)

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        bank_account_id = bank_account_1.id

        num_queries = self.num_queries
        num_queries += 1  # selectinload venue bank account links
        num_queries += 1  # selectinload invoices -> settlements
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params={"offererId": offerer_id, "bankAccountId": bank_account_id})

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["id"] == settlement_1.id

    def test_get_settlements_bank_account_filter_other_offerer(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        # the bank account is not linked to the user offerer
        bank_account = factories.BankAccountFactory()
        factories.SettlementFactory(status=models.SettlementStatus.EXECUTED, bankAccount=bank_account)

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        bank_account_id = bank_account.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id, "bankAccountId": bank_account_id})

        assert response.status_code == 200
        assert len(response.json) == 0

    def test_get_settlements_dates_filter(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        bank_account = factories.BankAccountFactory(offerer=user_offerer.offerer)
        _settlement_before = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__dateValidated=datetime.datetime.fromisoformat("2021-06-01"),
        )
        settlement_lower_bound = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__dateValidated=datetime.datetime.fromisoformat("2021-07-01"),
        )
        settlement_within = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__dateValidated=datetime.datetime.fromisoformat("2021-07-15"),
        )
        settlement_upper_bound = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__dateValidated=datetime.datetime.fromisoformat("2021-07-31"),
        )
        _settlement_after = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__dateValidated=datetime.datetime.fromisoformat("2021-08-01"),
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id

        num_queries = self.num_queries
        num_queries += 1  # selectinload venue bank account links
        num_queries += 1  # selectinload invoices -> settlements
        with testing.assert_num_queries(num_queries):
            response = client.get(
                URL,
                params={"offererId": offerer_id, "periodBeginningDate": "2021-07-01", "periodEndingDate": "2021-07-31"},
            )

        assert response.status_code == 200
        assert len(response.json) == 3
        assert {result["id"] for result in response.json} == {
            settlement_lower_bound.id,
            settlement_within.id,
            settlement_upper_bound.id,
        }

    def test_get_settlements_name_filter(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        bank_account = factories.BankAccountFactory(offerer=user_offerer.offerer)
        settlement_match_1 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__name="VIR123",
        )
        settlement_match_2 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__name="VIR123",
        )
        _settlement_no_match_1 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__name="VIR1",
        )
        _settlement_no_match_2 = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__name="VIR212",
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id

        num_queries = self.num_queries
        num_queries += 1  # selectinload venue bank account links
        num_queries += 1  # selectinload invoices -> settlements
        with testing.assert_num_queries(num_queries):
            response = client.get(
                URL,
                params={"offererId": offerer_id, "nameSearch": "VIR12"},
            )

        assert response.status_code == 200
        assert len(response.json) == 2
        assert {result["id"] for result in response.json} == {settlement_match_1.id, settlement_match_2.id}

    def test_no_access_to_offerer(self, client: TestClient):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        factories.SettlementFactory(bankAccount__offerer=offerer, status=models.SettlementStatus.EXECUTED)

        params = {"offererId": offerer.id}
        client = client.with_session_auth(user.email)

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # check if user_offerer exists
        num_queries += 1  # rollback
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
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

    def test_invalid_name_search(self, client: TestClient):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()

        params = {"offererId": offerer.id, "nameSearch": ""}
        client = client.with_session_auth(user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 400
        assert response.json == {
            "nameSearch": ["Cette chaîne de caractères doit avoir une taille minimum de 1 caractères"]
        }
