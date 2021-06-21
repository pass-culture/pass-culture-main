import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models


pytestmark = pytest.mark.usefixtures("db_session")


class FactoriesTest:
    def test_content_(self):
        instance = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.USER_PROFILING)
        assert isinstance(instance.resultContent, dict)

    def test_database_serialization(self):
        instance = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.USER_PROFILING)
        fraud_models.UserProfilingFraudData(**instance.resultContent)
