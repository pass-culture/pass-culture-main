import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.dms import api as dms_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
class DmsApiTest:
    def test_create_fraud_check(self):
        user = users_factories.UserFactory()
        application_number = 1

        fraud_check = subscription_api.initialize_identity_fraud_check(
            eligibility_type=user.eligibility,
            fraud_check_type=fraud_models.FraudCheckType.DMS,
            identity_content=None,
            third_party_id=str(application_number),
            user=user,
        )

        user_fraud_checks = user.beneficiaryFraudChecks
        assert len(user_fraud_checks) == 1
        assert user_fraud_checks[0] == fraud_check
        assert user_fraud_checks[0].thirdPartyId == str(application_number)
        assert user_fraud_checks[0].resultContent is None

    def test_get_fraud_check(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS, thirdPartyId=1)
        application_number = 1

        fraud_check = dms_api.get_fraud_check(user, application_number)

        user_fraud_checks = user.beneficiaryFraudChecks
        assert len(user_fraud_checks) == 1
        assert user_fraud_checks[0] == fraud_check
        assert user_fraud_checks[0].thirdPartyId == str(application_number)
        assert user_fraud_checks[0].eligibilityType == users_models.EligibilityType.AGE18
