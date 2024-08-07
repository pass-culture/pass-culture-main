import pytest

from pcapi.core import testing
import pcapi.core.finance.factories as finances_factories
import pcapi.core.finance.models as finances_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_bank_accounts_by_admin(client):
    bank_account_z = finances_factories.BankAccountFactory(label="Bank Account Z")
    bank_account_a = finances_factories.BankAccountFactory(label="Bank Account A")
    # Refused bank account
    finances_factories.BankAccountFactory(status=finances_models.BankAccountApplicationStatus.REFUSED)

    admin = users_factories.AdminFactory()

    client = client.with_session_auth(admin.email)
    # fetch session
    # fetch user
    # fetch bank_account
    with assert_num_queries(3):
        response = client.get("/finance/bank-accounts")
        assert response.status_code == 200

    bank_accounts = response.json
    assert len(bank_accounts) == 2
    assert bank_accounts[0] == {"id": bank_account_a.id, "label": "Bank Account A"}
    assert bank_accounts[1] == {"id": bank_account_z.id, "label": "Bank Account Z"}


def test_get_bank_accounts_by_pro(client):
    pro = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    bank_account_1 = finances_factories.BankAccountFactory(offerer=offerer, label="My first bank account")
    bank_account_2 = finances_factories.BankAccountFactory(offerer=offerer, label="My second bank account")
    # Refused bank account
    finances_factories.BankAccountFactory(offerer=offerer, status=finances_models.BankAccountApplicationStatus.REFUSED)
    # Accepted bank account in another offerer
    finances_models.BankAccount()

    client = client.with_session_auth(pro.email)
    with testing.assert_no_duplicated_queries():
        response = client.get("/finance/bank-accounts")

    assert response.status_code == 200
    bank_accounts = response.json
    assert len(bank_accounts) == 2
    assert bank_accounts[0] == {"id": bank_account_1.id, "label": "My first bank account"}
    assert bank_accounts[1] == {"id": bank_account_2.id, "label": "My second bank account"}
