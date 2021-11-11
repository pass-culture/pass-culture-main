import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.subscription.models as subscription_models


class BeneficiaryPreSubscriptionTest:
    def test_from_dms_data(self):
        dms_data = fraud_factories.DMSContentFactory()
        presubscriber = subscription_models.BeneficiaryPreSubscription.from_dms_source(dms_data)

        assert presubscriber.first_name == dms_data.first_name
        assert presubscriber.email == dms_data.email
