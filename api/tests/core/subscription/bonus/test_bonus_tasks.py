import datetime
from unittest.mock import call
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import tasks
from pcapi.models import db

from tests.core.subscription.bonus import bonus_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.connectors.api_particulier.get_quotient_familial")
def test_get_quotient_familial_task(mocked_get_quotient_familial):
    custodian = subscription_factories.QuotientFamilialCustodianFactory.create()
    fraud_check = subscription_factories.BonusFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED,
        resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory.build(
            custodian=custodian
        ).model_dump(),
    )
    fraud_check_id = fraud_check.id
    birth_date = fraud_check.user.validatedBirthDate
    mocked_get_quotient_familial.return_value = bonus_fixtures.QF_DESERIALIZED_RESPONSE

    payload = tasks.GetQuotientFamilialTaskPayload(fraud_check_id=fraud_check_id)
    tasks.apply_for_quotient_familial_bonus_task.delay(payload.model_dump())

    assert len(mocked_get_quotient_familial.mock_calls) == 12
    mocked_get_quotient_familial.assert_called_with(custodian, birth_date + relativedelta(years=17, months=11))

    fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check_id)
    assert fraud_check.status == subscription_models.FraudCheckStatus.KO
    assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]


@patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
def test_recover_started_quotient_familial_application(mocked_apply_for_qf_task):
    twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
    started_fraud_check_1 = subscription_factories.BonusFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED, updatedAt=twelve_hours_ago
    )
    started_fraud_check_2 = subscription_factories.BonusFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED, updatedAt=twelve_hours_ago - relativedelta(seconds=1)
    )

    tasks.recover_started_quotient_familial_application()

    mocked_apply_for_qf_task.assert_has_calls(
        [
            call(payload={"fraud_check_id": started_fraud_check_1.id}),
            call(payload={"fraud_check_id": started_fraud_check_2.id}),
        ],
        any_order=True,
    )


@patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
def test_recovery_ignores_recent_quotient_familial_application(mocked_apply_for_qf_task):
    twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
    subscription_factories.BonusFraudCheckFactory.create(
        status=subscription_models.FraudCheckStatus.STARTED, updatedAt=twelve_hours_ago + relativedelta(seconds=1)
    )

    tasks.recover_started_quotient_familial_application()

    mocked_apply_for_qf_task.assert_not_called()
