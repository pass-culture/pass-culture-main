import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.bonus import fraud_check_api
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class FirstAttemptDelayMeasureTest:
    def test_measures_the_delay_since_the_eighteenth_recredit(self):
        before = date_utils.get_naive_utc_now() - relativedelta(seconds=12345)
        with time_machine.travel(before):
            user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            reason=bonus_constants.QUOTIENT_FAMILIAL_ENDPOINT_ORIGIN,
        )

        first_attempt = fraud_check_api.get_first_manual_attempt(user)
        delay = fraud_check_api.get_attempt_delay_in_seconds(first_attempt)

        assert delay is not None
        assert 12345 <= delay <= 12500

    def test_only_the_first_application_is_measured(self):
        before = date_utils.get_naive_utc_now() - relativedelta(seconds=12345)
        with time_machine.travel(before):
            user = users_factories.BeneficiaryFactory()
            subscription_factories.BeneficiaryFraudCheckFactory.create(
                user=user,
                type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                status=subscription_models.FraudCheckStatus.KO,
                reason=bonus_constants.QUOTIENT_FAMILIAL_ENDPOINT_ORIGIN,
            )
        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.KO,
            reason=bonus_constants.DISABILITY_ENDPOINT_ORIGIN,
        )

        first_attempt = fraud_check_api.get_first_manual_attempt(user)
        delay = fraud_check_api.get_attempt_delay_in_seconds(first_attempt)

        assert delay is not None
        assert 0 <= delay <= 100

    def test_an_automatic_attempt_is_not_an_application(self):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            reason=f"{bonus_constants.AUTOMATIC_ORIGIN} through beneficiary activation",
        )

        assert fraud_check_api.get_first_manual_attempt(user) is None

    def test_no_delay_without_an_eighteenth_recredit(self):
        user = users_factories.UserFactory()

        assert fraud_check_api.get_first_manual_attempt(user) is None
