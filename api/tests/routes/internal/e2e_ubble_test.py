import pytest

import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class E2EUbbleIdentificationTest:
    def get_ubble_fraud_check_status(self, user):
        ubble_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.UBBLE
        ]
        if ubble_fraud_checks:
            return ubble_fraud_checks[0].status
        return None

    def test_user_is_identified_if_no_errors(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=17)
        client.with_token(user)
        response = client.post("/native/v1/ubble_identification/e2e", {})
        ubble_status = self.get_ubble_fraud_check_status(user)
        assert response.status_code == 204
        assert ubble_status == subscription_models.FraudCheckStatus.OK

    def test_user_is_not_identified_if_errors(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=17)
        client.with_token(user)
        response = client.post("/native/v1/ubble_identification/e2e", {"errors": [1201, 2201]})
        ubble_status = self.get_ubble_fraud_check_status(user)
        assert response.status_code == 204
        assert ubble_status in (
            subscription_models.FraudCheckStatus.KO,
            subscription_models.FraudCheckStatus.SUSPICIOUS,
        )
