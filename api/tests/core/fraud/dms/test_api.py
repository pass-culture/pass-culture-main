import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.dms.api import get_or_create_fraud_check
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
class DmsApiTest:
    def test_get_or_create_fraud_check_creates(self):
        user = users_factories.UserFactory()
        application_id = 1
        result_content = None

        fraud_check = get_or_create_fraud_check(user, application_id, result_content)

        user_fraud_checks = user.beneficiaryFraudChecks
        assert len(user_fraud_checks) == 1
        assert user_fraud_checks[0] == fraud_check
        assert user_fraud_checks[0].thirdPartyId == str(application_id)
        assert user_fraud_checks[0].resultContent == None

    def test_get_or_create_fraud_check_gets(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS, thirdPartyId=1)
        application_id = 1

        fraud_check = get_or_create_fraud_check(user, application_id)

        user_fraud_checks = user.beneficiaryFraudChecks
        assert len(user_fraud_checks) == 1
        assert user_fraud_checks[0] == fraud_check
        assert user_fraud_checks[0].thirdPartyId == str(application_id)
        assert user_fraud_checks[0].eligibilityType == users_models.EligibilityType.AGE18
