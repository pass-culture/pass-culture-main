from datetime import date
from unittest.mock import call
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.fraud.factories import BeneficiaryFraudCheckFactory
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.scripts.subscription.ubble.update_pending_ubble_applications import update_pending_ubble_applications


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.subscription.ubble.api.update_ubble_workflow")
def test_pending_and_created_fraud_checks_are_updated(update_ubble_workflow_mock):
    yesterday = date.today() - relativedelta(hours=13)
    created_fraud_check = BeneficiaryFraudCheckFactory(
        type=FraudCheckType.UBBLE, status=FraudCheckStatus.STARTED, dateCreated=yesterday
    )
    pending_fraud_check = BeneficiaryFraudCheckFactory(
        type=FraudCheckType.UBBLE, status=FraudCheckStatus.PENDING, dateCreated=yesterday
    )

    update_pending_ubble_applications()

    update_ubble_workflow_mock.assert_has_calls([call(created_fraud_check), call(pending_fraud_check)], any_order=True)
