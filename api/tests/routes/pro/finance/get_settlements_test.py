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
    num_queries += 1  # selectinload invoices

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
            invoices=[factories.InvoiceFactory(bankAccount=bank_account_2)],
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
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        # result is sorted by descending date
        assert response.json == [
            {
                "id": executed_settlement_2.id,
                "label": "VIR1",
                "date": batch_1.dateValidated.date().isoformat(),
                "amount": 200,
                "bankAccount": "account 2",
                "status": "executed",
                "invoicesCount": 1,
            },
            {
                "id": executed_settlement_1.id,
                "label": "VIR2",
                "date": batch_2.dateValidated.date().isoformat(),
                "amount": 100,
                "bankAccount": "account 1",
                "status": "executed",
                "invoicesCount": 0,
            },
            {
                "id": rejected_settlement.id,
                "label": "VIR3",
                "date": batch_3.dateValidated.date().isoformat(),
                "amount": 300,
                "bankAccount": "account 1",
                "status": "rejected",
                "invoicesCount": 0,
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
        with testing.assert_num_queries(self.num_queries):
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
        num_queries = self.num_queries
        num_queries -= 1  # no selectinload
        with testing.assert_num_queries(num_queries):
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
        settlement_within = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__dateValidated=datetime.datetime.fromisoformat("2021-07-01"),
        )
        _settlement_after = factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED,
            bankAccount=bank_account,
            batch__dateValidated=datetime.datetime.fromisoformat("2021-08-01"),
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(
                URL,
                params={"offererId": offerer_id, "periodBeginningDate": "2021-07-01", "periodEndingDate": "2021-07-31"},
            )

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["id"] == settlement_within.id

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
        with testing.assert_num_queries(self.num_queries):
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
