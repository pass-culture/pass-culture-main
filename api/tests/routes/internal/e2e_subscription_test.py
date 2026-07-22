from unittest.mock import call
from unittest.mock import patch

import pytest

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories


def test_recover_started_bonus_credit_applications_unauthorized(client):
    response = client.post("/e2e/bonus_credit/1/recover")

    assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
@patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
@patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
def test_recover_started_bonus_credit_applications_full_page(
    mocked_apply_for_aeeh_task, mocked_apply_for_aah_task, mocked_apply_for_qf_task, auth_client
):
    user = users_factories.BeneficiaryFactory()
    started_fraud_check_1 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED, user=user
    )
    started_fraud_check_2 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED, user=user
    )
    aah_fraud_check = subscription_factories.AAHBonusCreditFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED, user=user
    )
    aeeh_fraud_check = subscription_factories.AEEHBonusCreditFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED, user=user
    )

    response = auth_client.post(f"/e2e/bonus_credit/{user.id}/recover")

    assert response.status_code == 200
    assert response.json == {
        "aah_bonus_credit": [aah_fraud_check.id],
        "aeeh_bonus_credit": [aeeh_fraud_check.id],
        "qf_bonus_credit": [started_fraud_check_1.id, started_fraud_check_2.id],
    } or response.json == {
        "aah_bonus_credit": [aah_fraud_check.id],
        "aeeh_bonus_credit": [aeeh_fraud_check.id],
        "qf_bonus_credit": [started_fraud_check_2.id, started_fraud_check_1.id],
    }

    mocked_apply_for_qf_task.assert_has_calls(
        [
            call(payload={"fraud_check_id": started_fraud_check_1.id}),
            call(payload={"fraud_check_id": started_fraud_check_2.id}),
        ],
        any_order=True,
    )
    mocked_apply_for_aah_task.assert_has_calls([call(payload={"fraud_check_id": aah_fraud_check.id})])
    mocked_apply_for_aeeh_task.assert_has_calls([call(payload={"fraud_check_id": aeeh_fraud_check.id})])
