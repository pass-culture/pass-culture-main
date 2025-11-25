import datetime
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import tasks
from pcapi.core.users import models as users_models
from pcapi.models import db

from tests.core.subscription.bonus import bonus_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.connectors.api_particulier.get_quotient_familial")
def test_get_quotient_familial_task(mocked_get_quotient_familial):
    fraud_check = subscription_factories.BonusFraudCheckFactory(
        status=subscription_models.FraudCheckStatus.STARTED,
    )
    result_content = dict(fraud_check.resultContent)
    fraud_check_id = fraud_check.id
    birth_date = fraud_check.user.validatedBirthDate
    mocked_get_quotient_familial.return_value = bonus_fixtures.QF_DESERIALIZED_RESPONSE

    payload = tasks.GetQuotientFamilialTaskPayload(fraud_check_id=fraud_check_id)
    tasks.apply_for_quotient_familial_bonus_task.delay(payload.model_dump())

    assert len(mocked_get_quotient_familial.mock_calls) == 12
    mocked_get_quotient_familial.assert_called_with(
        last_name=result_content["custodian"]["last_name"],
        first_names=result_content["custodian"]["first_names"],
        common_name=None,
        birth_date=datetime.date.fromisoformat(result_content["custodian"]["birth_date"]),
        gender=users_models.GenderEnum(result_content["custodian"]["gender"]),
        country_insee_code="91100",
        city_insee_code="08480",
        quotient_familial_date=birth_date + relativedelta(years=16, months=11),
    )
    fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check_id)
    assert fraud_check.status == subscription_models.FraudCheckStatus.KO
    assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]
