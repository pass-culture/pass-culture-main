import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings

from tests.test_utils import run_command


@pytest.mark.usefixtures("db_session")
class BonusCreditRecoveryCommandTest:
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
