import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class BeneficiaryFraudListViewTest:
    def test_list_view(self, client):
        admin = users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        client.with_auth(admin.email)

        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudResultFactory(user=user)
        response = client.get("/pc/back-office/beneficiary_fraud/")
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class BeneficiaryFraudDetailViewTest:
    def test_detail_view(self, client):
        admin = users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudResultFactory(user=user)
        client.with_auth(admin.email)
        response = client.get("/pc/back-office/beneficiary_fraud/?id={user.id}")
        assert response.status_code == 200
