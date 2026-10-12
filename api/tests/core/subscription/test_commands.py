import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors import api_particulier
from pcapi.core.subscription import factories as subscription_factories

from tests.test_utils import run_command


@pytest.mark.fixtures("db_session")
class BonusCreditRecoveryCommandTest:
    @patch("pcapi.core.subscription.bonus.tasks.recover_started_bonus_credit_applications")
    def test_recovery_respects_retry_after_lock(self, mocked_recover_applications, requests_mock, app):
        # we got rate limited
        person = subscription_factories.BonusCreditPersonFactory.create()
        requests_mock.get(
            api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
            status_code=429,
            headers={"retry-after": "37"},
        )

        with pytest.raises(api_particulier.ParticulierApiRateLimitExceeded):
            api_particulier.get_quotient_familial(person)

        run_command(app, "recover_started_bonus_credit_applications", raise_on_error=True)

        mocked_recover_applications.assert_not_called()

    @patch("pcapi.core.subscription.bonus.tasks.recover_started_bonus_credit_applications")
    def test_recovery_respects_current_bandwidth_during_the_day(self, mocked_recover_applications, requests_mock, app):
        during_the_day = datetime.datetime(2026, 10, 10, 11, 0, 0)

        with time_machine.travel(during_the_day, tick=False):
            run_command(app, "recover_started_bonus_credit_applications", raise_on_error=True)

        mocked_recover_applications.assert_called_with(
            cutoff_time=datetime.datetime(2026, 10, 10, 11, 0),
            page_size=int(settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD * 0.5),
        )

    @patch("pcapi.core.subscription.bonus.tasks.recover_started_bonus_credit_applications")
    def test_recovery_ignores_current_bandwidth_during_the_night(self, mocked_recover_applications, requests_mock, app):
        during_the_night = datetime.datetime(2026, 10, 10, 1, 0, 0)

        with time_machine.travel(during_the_night, tick=False):
            run_command(app, "recover_started_bonus_credit_applications", raise_on_error=True)

        mocked_recover_applications.assert_called_with(
            cutoff_time=datetime.datetime(2026, 10, 10, 1, 0),
            page_size=int(settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD * 0.95),
        )
