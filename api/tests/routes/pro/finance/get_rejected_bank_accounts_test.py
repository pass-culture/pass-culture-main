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

URL = "/finance/rejected-bank-accounts"


class GetRejectedBankAccountsTest:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check if user_offerer exists
    num_queries += 1  # get settlements
    num_queries += 1  # selectinload bank account -> venue links
    num_queries += 1  # selectinload venue -> bank account links
    num_queries += 1  # selectinload invoices
    num_queries += 1  # selectinload invoices -> settlements

    def test_get_rejected_bank_accounts(self, client: TestClient):
        now = get_naive_utc_now()

        user_offerer = offerers_factories.UserOffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, pricing_point="self")
        venue_2 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, pricing_point="self")

        # one valid bank account with an executed settlement -> will not appear in the result
        bank_account_ok = factories.BankAccountFactory(offerer=user_offerer.offerer)
        factories.SettlementFactory(
            status=models.SettlementStatus.EXECUTED, amount=10000, bankAccount=bank_account_ok, batch__name="VIR1"
        )

        # bank account is refused, venues detached 5 days ago
        bank_account = factories.BankAccountFactory(
            offerer=user_offerer.offerer, label="Compte 1", status=models.BankAccountApplicationStatus.REFUSED
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_1,
            bankAccount=bank_account,
            timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_2,
            bankAccount=bank_account,
            timespan=[now - datetime.timedelta(days=365), now - datetime.timedelta(days=5)],
        )

        # the batch occurred 5 days ago and the settlement is rejected, in sync with the bank account status
        batch = factories.SettlementBatchFactory(name="VIR2", dateValidated=now - datetime.timedelta(days=5))
        invoice = factories.InvoiceFactory(amount=-10000, bankAccount=bank_account, date=batch.dateValidated)
        _settlement = factories.SettlementFactory(
            status=models.SettlementStatus.REJECTED,
            amount=10000,
            bankAccount=bank_account,
            batch=batch,
            invoices=[invoice],
        )

        # venue_2 is then linked to a valid bank account -> it will not appear in the response "detachedVenues"
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_2,
            bankAccount=bank_account_ok,
            timespan=[now - datetime.timedelta(days=4), None],
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id

        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        assert response.json == [
            {
                "id": bank_account.id,
                "label": "Compte 1",
                "obfuscatedIban": f"XXXX XXXX XXXX {bank_account.iban[-4:]}",
                "rejectedSettlementLabel": "VIR2",
                "detachedVenues": [{"id": venue_1.id, "publicName": venue_1.publicName}],
            },
        ]

    def test_no_access_to_offerer(self, client: TestClient):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()

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
