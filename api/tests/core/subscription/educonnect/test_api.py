import datetime

import freezegun
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
@freezegun.freeze_time("2022-11-02")
class EduconnectSubscriptionItemStatusTest:
    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))

        status = educonnect_subscription_api.get_educonnect_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, []
        )

        assert status == subscription_models.SubscriptionItemStatus.VOID

    def test_ko_and_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))

        ok_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.EDUCONNECT, status=fraud_models.FraudCheckStatus.OK
        )
        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.EDUCONNECT, status=fraud_models.FraudCheckStatus.KO
        )

        status = educonnect_subscription_api.get_educonnect_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [ok_check, ko_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.OK

    def test_ko(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2006, month=1, day=1))

        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.EDUCONNECT, status=fraud_models.FraudCheckStatus.KO
        )

        status = educonnect_subscription_api.get_educonnect_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [ko_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.TODO
