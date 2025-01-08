import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.finance import external
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance.backend.dummy import bank_accounts as dummy_bank_accounts
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db


pytestmark = [
    pytest.mark.usefixtures("db_session", "clean_dummy_backend_data"),
    pytest.mark.features(WIP_ENABLE_NEW_FINANCE_WORKFLOW=True, ENABLE_BANK_ACCOUNT_SYNC=True),
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


class ExternalFinanceCommandTest:
    def test_push_bank_accounts_command(self, run_command, mocker):
        with patch("pcapi.core.finance.external.push_bank_accounts") as push_bank_accounts_mock:
            run_command("push_bank_accounts", raise_on_error=True)

        assert push_bank_accounts_mock.call_count == 1

    @pytest.mark.parametrize(
        "enable_new_finance_workflow,enable_bank_account_sync", [(False, True), (True, False), (False, False)]
    )
    def test_push_bank_accounts_command_feature_toggle(
        self, features, run_command, enable_new_finance_workflow, enable_bank_account_sync
    ):
        features.ENABLE_BANK_ACCOUNT_SYNC = enable_bank_account_sync
        features.WIP_ENABLE_NEW_FINANCE_WORKFLOW = enable_new_finance_workflow
        with patch("pcapi.core.finance.external.push_bank_accounts") as push_bank_accounts_mock:
            run_command("push_bank_accounts", raise_on_error=True)

        assert push_bank_accounts_mock.call_count == 0
