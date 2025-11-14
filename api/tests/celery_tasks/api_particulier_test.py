import datetime
from unittest.mock import patch

import pytest

from pcapi.celery_tasks import api_particulier as tasks
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.connectors.api_particulier.get_quotient_familial")
def test_get_quotient_familial_task(mocked_get_quotient_familial):
    fraud_check = subscription_factories.BonusFraudCheckFactory(
        status=subscription_models.FraudCheckStatus.STARTED,
    )
    result_content = dict(fraud_check.resultContent)
    fraud_check_id = fraud_check.id
    fraud_check_date_created = fraud_check.dateCreated

    payload = tasks.GetQuotientFamilialTaskPayload(fraud_check_id=fraud_check_id)

    tasks.get_quotient_familial_task(payload)
    mocked_get_quotient_familial.assert_called_once()
    mocked_get_quotient_familial.assert_called_with(
        last_name=result_content["custodian"]["last_name"],
        first_names=result_content["custodian"]["first_names"],
        birth_date=datetime.date.fromisoformat(result_content["custodian"]["birth_date"]),
        gender=users_models.GenderEnum[result_content["custodian"]["gender"]],
        country_insee_code="91100",
        city_insee_code="08480",
        quotient_familial_date=fraud_check_date_created.date(),
    )
    fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check_id)
    assert fraud_check.status == subscription_models.FraudCheckStatus.OK
