import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.ubble.models as ubble_fraud_models


pytestmark = pytest.mark.usefixtures("db_session")


class FactoriesTest:
    @pytest.mark.parametrize(
        "check_type,model_class",
        [
            (fraud_models.FraudCheckType.DMS, fraud_models.DMSContent),
            (fraud_models.FraudCheckType.USER_PROFILING, fraud_models.UserProfilingFraudData),
            (fraud_models.FraudCheckType.UBBLE, ubble_fraud_models.UbbleContent),
            (fraud_models.FraudCheckType.EDUCONNECT, fraud_models.EduconnectContent),
        ],
    )
    def test_database_serialization(self, check_type, model_class):
        instance = fraud_factories.BeneficiaryFraudCheckFactory(type=check_type)
        model_class(**instance.resultContent)

    @pytest.mark.parametrize(
        "check_type,factory_class",
        [
            (fraud_models.FraudCheckType.DMS, fraud_factories.DMSContentFactory),
            (fraud_models.FraudCheckType.USER_PROFILING, fraud_factories.UserProfilingFraudDataFactory),
            (fraud_models.FraudCheckType.UBBLE, fraud_factories.UbbleContentFactory),
            (fraud_models.FraudCheckType.EDUCONNECT, fraud_factories.EduconnectContentFactory),
        ],
    )
    def test_database_overwrite(self, check_type, factory_class):
        content = factory_class()
        instance = fraud_factories.BeneficiaryFraudCheckFactory(type=check_type, resultContent=content)
        serialized_data = factory_class._meta.model(**instance.resultContent)

        assert content == serialized_data
