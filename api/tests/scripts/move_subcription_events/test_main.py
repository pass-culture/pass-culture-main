from unittest.mock import patch

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.scripts.move_subscription_events.main import move_subscription_and_credit_destination_account
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
@patch("pcapi.scripts.move_subscription_events.main.read_user_ids_from_csv")
def test_subscription_move_and_activation(read_csv_mock):
    last_year = date_utils.get_naive_utc_now() - relativedelta(years=1)
    with time_machine.travel(last_year):
        credited_account = users_factories.BeneficiaryFactory(age=17)

    duplicate_account = users_factories.UserFactory(age=18, _phoneNumber="+33123456789")
    _profile_fraud_check = subscription_factories.ProfileCompletionFraudCheckFactory(
        user=duplicate_account, eligibilityType=users_models.EligibilityType.AGE17_18
    )
    _identity_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
        user=duplicate_account,
        eligibilityType=users_models.EligibilityType.AGE17_18,
        type=subscription_models.FraudCheckType.UBBLE,
        status=subscription_models.FraudCheckStatus.SUSPICIOUS,
        reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
    )
    _honor_fraud_check = subscription_factories.HonorStatementFraudCheckFactory(
        user=duplicate_account, eligibilityType=users_models.EligibilityType.AGE17_18
    )

    read_csv_mock.return_value = [(str(duplicate_account.id), str(credited_account.id))]

    next_year = date_utils.get_naive_utc_now() + relativedelta(years=1)
    with time_machine.travel(next_year):
        move_subscription_and_credit_destination_account(
            from_user=duplicate_account, to_user=credited_account, author_id=None, should_update_external_user=False
        )

    assert credited_account.received_pass_18_v3
