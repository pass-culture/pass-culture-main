import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models


pytestmark = pytest.mark.usefixtures("db_session")


class FactoriesTest:
    @pytest.mark.parametrize(
        "check_type,instance_type",
        [
            (fraud_models.FraudCheckType.USER_PROFILING, fraud_models.UserProfilingFraudData),
            (fraud_models.FraudCheckType.JOUVE, fraud_models.JouveContent),
        ],
    )
    def test_database_serialization(self, check_type, instance_type):
        instance = fraud_factories.BeneficiaryFraudCheckFactory(type=check_type)
        instance_type(**instance.resultContent)

    def test_database_overwrite(self):
        content = fraud_factories.JouveContentFactory()
        instance = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.JOUVE, resultContent=content
        )
        serialized_data = fraud_models.JouveContent(**instance.resultContent)

        assert content == serialized_data
